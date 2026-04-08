import sys
from unittest.mock import MagicMock
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()
sys.modules['google.cloud.firestore_v1'] = MagicMock()

from shared.firestore_client import bulk_job_exists, save_jobs
from shared.models import Job, JobSource

print("Compiled successfully!")
