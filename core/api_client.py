#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DashScope API 客户端
负责与阿里云 DashScope API 交互
"""

import base64
import json
import os
import requests
from typing import Dict, Optional
from config.settings import settings


class DashScopeClient:
    """DashScope API 客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.api_key = settings.get_api_key()
        self.base_url = settings.DASHSCOPE_BASE_URL
    
    def _get_headers(self, async_mode=False, oss_resource_resolve=False):
        """获取请求头"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        if async_mode:
            headers['X-DashScope-Async'] = 'enable'
        if oss_resource_resolve:
            headers['X-DashScope-OssResourceResolve'] = 'enable'
        return headers
    
    def submit_task(self, image_path: str, prompt: str, model: str, 
                   resolution: str, negative_prompt: str = "",
                   prompt_extend: bool = True, duration: int = 5,
                   shot_type: str = None) -> Dict:
        """
        提交图生视频任务
        
        Args:
            image_path: 图片文件路径
            prompt: 提示词
            model: 模型名称
            resolution: 分辨率
            negative_prompt: 反向提示词
            prompt_extend: 是否启用智能改写
            duration: 视频时长（秒）
            shot_type: 镜头类型（仅2.6模型支持，multi/single）
            
        Returns:
            API 响应数据
        """
        # 读取图片并转换为 base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 准备请求数据
        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "img_url": f"data:image/jpeg;base64,{image_data}"
            },
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend,
                "duration": duration
            }
        }
        
        # 添加反向提示词
        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
        
        # 添加镜头类型（仅2.6模型支持，且仅在启用提示词扩展时生效）
        if shot_type and prompt_extend:
            payload["parameters"]["shot_type"] = shot_type
        
        # 发送请求
        response = requests.post(
            f'{self.base_url}/services/aigc/video-generation/video-synthesis',
            headers=self._get_headers(async_mode=True),
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(
                f"API 调用失败: {error_data.get('message', '未知错误')} "
                f"(状态码: {response.status_code})"
            )
    
    def query_task(self, async_task_id: str) -> Dict:
        """
        查询任务状态
        
        Args:
            async_task_id: 异步任务 ID
            
        Returns:
            任务状态数据
        """
        response = requests.get(
            f'{self.base_url}/tasks/{async_task_id}',
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise Exception('任务不存在')
        else:
            raise Exception(f'查询失败 (状态码: {response.status_code})')
    
    def download_video(self, video_url: str, output_path: str) -> str:
        """
        下载视频文件
        
        Args:
            video_url: 视频 URL
            output_path: 输出路径(文件夹或完整文件路径)
            
        Returns:
            下载后的文件路径
        """
        try:
            # 判断 output_path 是文件夹还是文件
            if os.path.isdir(output_path):
                # 如果是文件夹,生成文件名
                import time
                timestamp = int(time.time() * 1000)
                filename = f"video_{timestamp}.mp4"
                full_path = os.path.join(output_path, filename)
            else:
                # 如果是完整路径,直接使用
                full_path = output_path
            
            # 下载视频
            response = requests.get(video_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(full_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return full_path
            else:
                raise Exception(f"下载失败: HTTP {response.status_code}")
        except Exception as e:
            raise Exception(f"下载视频失败: {str(e)}")
    
    def submit_image_edit(self, images: list, prompt: str, model: str = 'qwen-image-edit-plus',
                         n: int = 2, negative_prompt: str = "", prompt_extend: bool = True, size: str = "",
                         enable_interleave: bool = False, max_images: int = 5) -> Dict:
        """
        提交图像编辑任务（单图编辑或多图融合）
        
        Args:
            images: 图片路径列表（单图或多图）
            prompt: 编辑提示词
            model: 模型名称
            n: 生成图片数量（1-6）
            negative_prompt: 反向提示词
            prompt_extend: 是否启用智能改写
            
        Returns:
            API 响应数据
        """
        # 判断是否为万相模型（使用异步API）
        is_wanxiang = model.startswith('wan2.') or model == 'wan2.6-image'
        
        if is_wanxiang:
            # 万相2.5/2.6使用异步API
            return self._submit_wanxiang_image_edit(images, prompt, model, n, prompt_extend, size, enable_interleave, max_images)
        else:
            # 其他模型使用同步API
            return self._submit_qwen_image_edit(images, prompt, model, n, negative_prompt, prompt_extend)
    
    def _submit_qwen_image_edit(self, images: list, prompt: str, model: str,
                               n: int, negative_prompt: str, prompt_extend: bool) -> Dict:
        """提交通义千问图像编辑任务（同步）"""
        # 准备消息内容
        content = []
        
        # 添加所有图片
        for image_path in images:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            ext = image_path.lower().split('.')[-1]
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'bmp': 'image/bmp',
                'tiff': 'image/tiff',
                'webp': 'image/webp',
                'gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            content.append({
                "image": f"data:{mime_type};base64,{image_data}"
            })
        
        # 添加提示词
        content.append({
            "text": prompt
        })
        
        # 准备请求数据
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            },
            "parameters": {
                "n": n,
                "negative_prompt": negative_prompt if negative_prompt else " ",
                "prompt_extend": prompt_extend,
                "watermark": False
            }
        }
        
        # 发送请求
        response = requests.post(
            f'{self.base_url}/services/aigc/multimodal-generation/generation',
            headers=self._get_headers(),
            data=json.dumps(payload),
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(
                f"API 调用失败: {error_data.get('message', '未知错误')} "
                f"(状态码: {response.status_code})"
            )
    
    def _submit_wanxiang_image_edit(self, images: list, prompt: str, model: str,
                                   n: int, prompt_extend: bool, size: str = "",
                                   enable_interleave: bool = False, max_images: int = 5) -> Dict:
        """提交万相图像编辑任务（异步，支持2.5和2.6）"""
        # 准备图片URL列表
        image_urls = []
        for image_path in images:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            ext = image_path.lower().split('.')[-1]
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'bmp': 'image/bmp',
                'tiff': 'image/tiff',
                'webp': 'image/webp',
                'gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            image_urls.append(f"data:{mime_type};base64,{image_data}")
        
        # 判断是否为万相2.6
        is_wan26 = model == 'wan2.6-image'
        
        if is_wan26:
            # 万相2.6使用新的image-generation接口和messages格式
            content = [{"text": prompt}]
            # 添加图片到content
            for image_url in image_urls:
                content.append({"image": image_url})
            
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": content
                        }
                    ]
                },
                "parameters": {
                    "n": n if not enable_interleave else 1,  # 图文混合模式下n固定为1
                    "watermark": False
                }
            }
            
            # 添加prompt_extend参数（仅在非图文混合模式下生效）
            if not enable_interleave:
                payload["parameters"]["prompt_extend"] = prompt_extend
            
            # 添加size参数（如果指定）
            if size:
                payload["parameters"]["size"] = size
            else:
                payload["parameters"]["size"] = "1280*1280"  # 默认尺寸
            
            # 添加图文混合参数
            if enable_interleave:
                payload["parameters"]["enable_interleave"] = True
                payload["parameters"]["max_images"] = max_images
            
            # 万相2.6使用新接口
            url = f'{self.base_url}/services/aigc/image-generation/generation'
        else:
            # 万相2.5使用旧格式
            payload = {
                "model": model,
                "input": {
                    "prompt": prompt,
                    "images": image_urls
                },
                "parameters": {
                    "n": n,
                    "prompt_extend": prompt_extend
                }
            }
            
            # 添加size参数（如果指定）
            if size:
                payload["parameters"]["size"] = size
            
            # 万相2.5使用旧接口
            url = f'{self.base_url}/services/aigc/image2image/image-synthesis'
        
        # 发送异步请求
        response = requests.post(
            url,
            headers=self._get_headers(async_mode=True),
            data=json.dumps(payload),
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(
                f"API 调用失败: {error_data.get('message', '未知错误')} "
                f"(状态码: {response.status_code})"
            )
    
    def query_image_edit_task(self, task_id: str) -> Dict:
        """查询图像编辑任务状态"""
        return self.query_task(task_id)
    
    def upload_video_and_get_url(self, video_path: str, model_name: str) -> str:
        """
        上传视频文件并获取临时URL
        
        Args:
            video_path: 视频文件路径
            model_name: 模型名称
            
        Returns:
            临时HTTP URL
        """
        from pathlib import Path
        
        # 1. 获取上传凭证
        url = f"{self.base_url}/uploads"
        headers = self._get_headers()
        params = {
            "action": "getPolicy",
            "model": model_name
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"获取上传凭证失败: {response.text}")
        
        policy_data = response.json()['data']
        
        # 2. 上传文件到OSS
        file_name = Path(video_path).name
        key = f"{policy_data['upload_dir']}/{file_name}"
        
        with open(video_path, 'rb') as file:
            files = {
                'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
                'Signature': (None, policy_data['signature']),
                'policy': (None, policy_data['policy']),
                'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
                'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
                'key': (None, key),
                'success_action_status': (None, '200'),
                'file': (file_name, file)
            }
            response = requests.post(policy_data['upload_host'], files=files)
            if response.status_code != 200:
                raise Exception(f"上传文件失败: {response.text}")
        
        # 3. 返回oss://格式的URL
        # API服务端会自己处理OSS访问权限
        # 不需要转换为HTTP URL，因为HTTP URL可能没有访问权限
        oss_url = f"oss://{key}"
        
        return oss_url
    
    def submit_reference_video_to_video(self, reference_video_urls: list, prompt: str,
                                       negative_prompt: str = "", size: str = "1920*1080",
                                       duration: int = 5, shot_type: str = "single",
                                       audio: bool = True, seed: int = None) -> Dict:
        """
        提交参考生视频任务
        
        Args:
            reference_video_urls: 参考视频URL列表（1-2个）
            prompt: 提示词
            negative_prompt: 反向提示词
            size: 分辨率（如 1280*720）
            duration: 视频时长（5或10秒）
            shot_type: 镜头类型（single/multi）
            audio: 是否包含音频
            seed: 随机种子
            
        Returns:
            API 响应数据
        """
        # 准备请求数据
        payload = {
            "model": "wan2.6-r2v",
            "input": {
                "prompt": prompt,
                "reference_video_urls": reference_video_urls
            },
            "parameters": {
                "size": size,
                "duration": duration,
                "audio": audio,
                "shot_type": shot_type
            }
        }
        
        # 添加反向提示词
        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
        
        # 添加随机种子
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        # 发送异步请求
        # 使用oss://格式的URL时，需要启用OSS资源解析
        response = requests.post(
            f'{self.base_url}/services/aigc/video-generation/video-synthesis',
            headers=self._get_headers(async_mode=True, oss_resource_resolve=True),
            data=json.dumps(payload),
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(
                f"API 调用失败: {error_data.get('message', '未知错误')} "
                f"(状态码: {response.status_code})"
            )
    
    def submit_keyframe_to_video(self, first_frame_url: str, last_frame_url: str,
                                prompt: str, model: str = 'wan2.2-kf2v-flash',
                                resolution: str = '720P', prompt_extend: bool = True) -> Dict:
        """
        提交首尾帧生成视频任务
        
        Args:
            first_frame_url: 首帧图片URL(Base64编码)
            last_frame_url: 尾帧图片URL(Base64编码)
            prompt: 视频描述
            model: 模型名称
            resolution: 分辨率(480P/720P/1080P)
            prompt_extend: 是否启用智能改写
            
        Returns:
            API 响应数据
        """
        # 准备请求数据
        payload = {
            "model": model,
            "input": {
                "first_frame_url": first_frame_url,
                "last_frame_url": last_frame_url,
                "prompt": prompt
            },
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend
            }
        }
        
        # 发送异步请求
        response = requests.post(
            f'{self.base_url}/services/aigc/image2video/video-synthesis',
            headers=self._get_headers(async_mode=True),
            data=json.dumps(payload),
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            raise Exception(
                f"API 调用失败: {error_data.get('message', '未知错误')} "
                f"(状态码: {response.status_code})"
            )
