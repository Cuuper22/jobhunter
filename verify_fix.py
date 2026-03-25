import sys
from unittest.mock import MagicMock
from collections import namedtuple

# Mock required modules
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()

# Mock Google Cloud Firestore
mock_firestore_v1 = MagicMock()
mock_firestore_v1.FieldFilter = MagicMock()
sys.modules['google.cloud.firestore_v1'] = mock_firestore_v1

# Important: Need to replace db client from shared.firestore_client
from shared.firestore_client import get_existing_job_urls, save_jobs, db

def test_get_existing_job_urls():
    print("Testing get_existing_job_urls...")

    # Setup mock returns
    mock_collection = MagicMock()
    db.collection.return_value = mock_collection

    mock_where = MagicMock()
    mock_collection.where.return_value = mock_where

    mock_select = MagicMock()
    mock_where.select.return_value = mock_select

    # Mock document containing 'url' dictionary
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {"url": "http://existing.com/job1"}
    mock_select.get.return_value = [mock_doc]

    # Run test
    urls_to_check = ["http://existing.com/job1", "http://new.com/job2"]
    existing = get_existing_job_urls(urls_to_check)

    assert "http://existing.com/job1" in existing
    assert "http://new.com/job2" not in existing

    # Assert query structure called
    db.collection.assert_called_with("jobs")
    mock_collection.where.assert_called()
    mock_where.select.assert_called_with(["url"])
    print("Test get_existing_job_urls PASSED")

def test_save_jobs():
    print("Testing save_jobs...")

    # Setup mock batch and doc
    mock_batch = MagicMock()
    db.batch.return_value = mock_batch

    mock_collection = MagicMock()
    db.collection.return_value = mock_collection

    mock_doc_ref = MagicMock()
    mock_doc_ref.id = "mock_id_123"
    mock_collection.document.return_value = mock_doc_ref

    # Create mock jobs
    JobMock = namedtuple("JobMock", ["model_dump", "id"])
    mock_job_1 = MagicMock()
    mock_job_1.model_dump.return_value = {"title": "Test 1"}

    mock_job_2 = MagicMock()
    mock_job_2.model_dump.return_value = {"title": "Test 2"}

    # Run test
    job_ids = save_jobs([mock_job_1, mock_job_2])

    # Assert
    assert len(job_ids) == 2
    assert "mock_id_123" in job_ids
    assert mock_batch.set.call_count == 2
    mock_batch.commit.assert_called_once()
    print("Test save_jobs PASSED")

if __name__ == "__main__":
    test_get_existing_job_urls()
    test_save_jobs()
