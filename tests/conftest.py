"""Shared fixtures for JobPacker tests."""

import json
from datetime import datetime

import pandas as pd
import pytest


@pytest.fixture
def default_config():
    """Return the default configuration dict."""
    return {
        "default_search": "",
        "default_location": "USA",
        "results_per_site": 15,
        "remote_only": False,
        "job_type": None,
        "job_boards": ["indeed", "linkedin", "glassdoor", "zip_recruiter", "google"],
    }


@pytest.fixture
def custom_config():
    """Return a customized configuration dict."""
    return {
        "default_search": "python developer",
        "default_location": "New York, NY",
        "results_per_site": 25,
        "remote_only": True,
        "job_type": "fulltime",
        "job_boards": ["indeed", "linkedin"],
    }


@pytest.fixture
def config_file(tmp_path, custom_config):
    """Create a temporary config file and return its path."""
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(custom_config, f)
    return config_path


@pytest.fixture
def sample_jobspy_jobs():
    """Return sample jobs in jobspy DataFrame format."""
    return [
        {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "job_url": "https://example.com/job/123",
            "description": "Looking for a senior Python developer...",
            "date_posted": datetime(2025, 1, 15),
            "min_amount": 120000,
            "max_amount": 180000,
            "site": "indeed",
        },
        {
            "title": "Data Engineer",
            "company": "Data Inc",
            "location": "Remote",
            "job_url": "https://example.com/job/456",
            "description": "Data engineering role with cloud experience...",
            "date_posted": "2025-01-10",
            "min_amount": 100000,
            "max_amount": 150000,
            "site": "linkedin",
        },
        {
            "title": "Junior Developer",
            "company": "StartupXYZ",
            "location": "Austin, TX",
            "job_url": "https://example.com/job/789",
            "description": "Entry level position...",
            "date_posted": None,
            "min_amount": float("nan"),
            "max_amount": float("nan"),
            "site": "glassdoor",
        },
        {
            "title": "Software Engineer",
            "company": "BigTech",
            "location": "Seattle, WA",
            "job_url": "https://example.com/job/101",
            "description": "Full stack development...",
            "date_posted": datetime(2025, 1, 20),
            "min_amount": 90000,
            "max_amount": None,
            "site": "zip_recruiter",
        },
    ]


@pytest.fixture
def sample_jobspy_dataframe(sample_jobspy_jobs):
    """Return sample jobs as a pandas DataFrame (as jobspy returns)."""
    return pd.DataFrame(sample_jobspy_jobs)


@pytest.fixture
def expected_cleansheet_job():
    """Return expected structure of a Cleansheet-format job."""
    return {
        "id": str,  # UUID string
        "company": str,
        "title": str,
        "location": str,
        "url": str,
        "description": str,
        "salary": str,
        "datePosted": str,  # YYYY-MM-DD format
        "source": str,
        "status": "Saved",
        "tags": list,
    }


@pytest.fixture
def mock_console(mocker):
    """Mock the rich console to prevent actual output."""
    return mocker.patch("jobpacker.console")


@pytest.fixture
def mock_prompt(mocker):
    """Mock rich Prompt.ask to return predefined values."""
    return mocker.patch("jobpacker.Prompt.ask")


@pytest.fixture
def mock_scrape_jobs(mocker, sample_jobspy_dataframe):
    """Mock jobspy.scrape_jobs to return sample data."""
    mock = mocker.patch("jobpacker.scrape_jobs")
    mock.return_value = sample_jobspy_dataframe
    return mock
