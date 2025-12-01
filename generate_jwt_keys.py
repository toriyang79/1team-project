"""
JWT RS256 키 페어 생성 스크립트

개발용 임시 키를 생성합니다.
운영 환경에서는 Django Auth 서버에서 제공하는 실제 Public Key를 사용해야 합니다.
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_rsa_keypair():
    """RSA 키 페어 생성 (2048비트)"""

    # Private Key 생성
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Private Key를 PEM 형식으로 직렬화
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Public Key 추출
    public_key = private_key.public_key()

    # Public Key를 PEM 형식으로 직렬화
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

if __name__ == "__main__":
    print("=" * 60)
    print("JWT RS256 키 페어 생성")
    print("=" * 60)

    private_key, public_key = generate_rsa_keypair()

    # Private Key 저장 (Django Auth 서버용 - 참고용)
    with open("jwt_private_key.pem", "w") as f:
        f.write(private_key)
    print("\n✅ Private Key 저장됨: jwt_private_key.pem")
    print("   (이 키는 Django Auth 서버에서 사용됩니다)")

    # Public Key 저장 (FastAPI 서버용)
    with open("jwt_public_key.pem", "w") as f:
        f.write(public_key)
    print("✅ Public Key 저장됨: jwt_public_key.pem")
    print("   (이 키를 .env 파일의 JWT_PUBLIC_KEY에 복사하세요)")

    print("\n" + "=" * 60)
    print("Public Key 내용 (.env 파일에 복사하세요):")
    print("=" * 60)
    print(public_key)

    print("\n" + "=" * 60)
    print("⚠️  중요 사항:")
    print("=" * 60)
    print("1. 이 키는 개발용 임시 키입니다")
    print("2. 운영 환경에서는 Django Auth 서버의 실제 Public Key를 사용하세요")
    print("3. Private Key는 절대 공유하지 마세요 (.gitignore에 추가됨)")
    print("4. Public Key만 FastAPI 서버의 .env 파일에 설정하세요")
