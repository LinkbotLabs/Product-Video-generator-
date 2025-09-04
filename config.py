import os
from dotenv import load_dotenv

class Config:
    @staticmethod
    def load_env(env_file=".env"):
        """Load environment variables from the specified .env file."""
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file)
            print(f"🔧 Loaded environment from {env_file}")
        else:
            print(f"⚠️ {env_file} not found, falling back to system environment variables")
        
        # Set ImageMagick path here (update the path accordingly)
        os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
        print(f"🔧 Set IMAGEMAGICK_BINARY to {os.environ['IMAGEMAGICK_BINARY']}")

    @staticmethod
    def get_amazon_tag():
        return os.getenv("AMAZON_AFFILIATE_TAG", "demo-affiliate-tag")

    @staticmethod
    def get_youtube_key():
        return os.getenv("YOUTUBE_API_KEY", "")

    @staticmethod
    def get_license_key():
        return os.getenv("LICENSE_KEY", "")

    @staticmethod
    def is_activated():
        return bool(Config.get_license_key())

