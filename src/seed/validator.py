"""
连续性验证器
"""

import hashlib
from typing import Tuple
from .seed import Seed


class ContinuityValidator:
    """连续性验证器 - 验证种子完整性"""

    def __init__(self, seed: Seed):
        self.seed = seed
        self.original_hash = seed.hash
        self.original_uuid = seed.uuid

    def validate(self) -> Tuple[bool, str]:
        """验证种子完整性"""
        # 1. 验证UUID
        if self.seed.uuid != self.original_uuid:
            return False, "UUID不匹配: 种子身份失效"

        # 2. 验证哈希 (不包含hash字段本身)
        current_hash = self.seed.calculate_hash(include_hash=False)
        if current_hash != self.original_hash:
            return False, f"哈希不匹配: 种子被篡改 (expected: {current_hash[:16]}, got: {self.original_hash[:16]})"

        # 3. 验证必要字段
        if not self.seed.identity.name:
            return False, "身份名称缺失"

        return True, "验证通过"

    def get_signature(self) -> dict:
        """获取种子签名"""
        return {
            "uuid": self.seed.uuid,
            "hash": self.seed.hash,
            "name": self.seed.identity.name,
            "validated_at": self.seed.updated_at,
        }
