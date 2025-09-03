#!/usr/bin/env python3
"""
Generate JWT keys and JWKS file for StackRox MCP server authentication.
"""

import argparse
import base64
import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_rsa_keypair():
    """Generate RSA private/public key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def get_jwk_from_public_key(public_key, kid="jwtk0"):
    """Convert public key to JWK format."""
    public_numbers = public_key.public_numbers()

    # Convert to base64url encoding
    def int_to_base64url(num):
        byte_length = (num.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(num.to_bytes(byte_length, 'big')).decode('ascii').rstrip('=')

    jwk = {
        "kty": "RSA",
        "use": "sig",
        "kid": kid,
        "alg": "RS256",
        "n": int_to_base64url(public_numbers.n),
        "e": int_to_base64url(public_numbers.e)
    }

    return jwk


def save_private_key(private_key, filename="private_key.pem"):
    """Save private key to PEM file."""
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(filename, 'wb') as f:
        f.write(pem)

    print(f"Private key saved to {filename}")


def create_jwks_file(public_key, filename="jwks.json"):
    """Create JWKS file with public key."""
    jwk = get_jwk_from_public_key(public_key)

    jwks = {
        "keys": [jwk]
    }

    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(jwks, f, indent=2)

    print(f"JWKS file saved to {filename}")
    return jwks


def generate_jwks_from_existing_key(private_key_path="private_key.pem", jwks_path="jwks.json"):
    """Generate JWKS file from existing private key."""
    if not os.path.exists(private_key_path):
        print(f"❌ Private key file not found: {private_key_path}")
        return False

    try:
        # Load existing private key
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

        public_key = private_key.public_key()

        # Create JWKS file
        jwks = create_jwks_file(public_key, jwks_path)

        print(f"✅ JWKS generated from existing private key: {private_key_path}")
        print(f"📄 JWKS saved to: {jwks_path}")
        print("\nJWKS content:")
        print(json.dumps(jwks, indent=2))

        return True

    except Exception as e:
        print(f"❌ Error loading private key: {e}")
        return False


def main():
    """ Main """
    parser = argparse.ArgumentParser(description="Generate JWKS from RSA private key")
    parser.add_argument("--private-key", "-k",
                       help="Path to private key file (default: private_key.pem)",
                       default="private_key.pem")
    parser.add_argument("--from-existing", action="store_true",
                       help="Generate JWKS from existing private key")

    args = parser.parse_args()

    if args.from_existing:
        print("Generating JWKS from existing private key...")
        # Create build directory
        build_dir = "build"
        os.makedirs(build_dir, exist_ok=True)

        jwks_path = os.path.join(build_dir, "jwks.json")
        generate_jwks_from_existing_key(args.private_key, jwks_path)
    else:
        print("Generating RSA key pair for JWT authentication...")

        # Create build directory
        build_dir = "build"
        os.makedirs(build_dir, exist_ok=True)

        # Generate key pair
        private_key, public_key = generate_rsa_keypair()

        # Save private key in build directory
        private_key_path = os.path.join(build_dir, "private_key.pem")
        save_private_key(private_key, private_key_path)

        # Create JWKS file in build directory
        jwks_path = os.path.join(build_dir, "jwks.json")
        jwks = create_jwks_file(public_key, jwks_path)

        print("\nGenerated files:")
        print(f"- {private_key_path}: Private key for signing JWTs")
        print(f"- {jwks_path}: Public key set for JWT verification")

        print("\nJWKS content:")
        print(json.dumps(jwks, indent=2))

        print("\nTo use these keys:")
        print("1. Keep private_key.pem secure and use it to sign JWTs")
        print("2. Make jwks.json available at the JWKS URI endpoint")
        print("3. Update environment variables:")
        print("   FASTMCP_SERVER_AUTH_JWT_JWKS_URI=http://localhost:8000/jwks.json")
        print("   FASTMCP_SERVER_AUTH_JWT_ISSUER=stackrox-mcp-server")
        print("   FASTMCP_SERVER_AUTH_JWT_AUDIENCE=stackrox-mcp")

        print("\nTo generate JWKS from existing private key, run:")
        print("   python generate_jwks.py --from-existing --private-key path/to/key.pem")


if __name__ == "__main__":
    main()
