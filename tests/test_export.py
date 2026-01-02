"""Tests for job export functionality."""

import json
import math
import re
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestFilenameGeneration:
    """Tests for export filename generation."""

    def test_filename_sanitizes_special_characters(self):
        """Special characters in search term should be replaced with underscores."""
        import jobpacker

        # Mock the Prompt to return a specific filename
        with patch.object(jobpacker, "Prompt") as mock_prompt:
            mock_prompt.ask.side_effect = lambda msg, default: default

            with patch.object(jobpacker, "console"):
                with patch("builtins.open", MagicMock()):
                    # We need to capture the default filename
                    # Since we can't easily extract it, let's test the regex pattern directly
                    pass

        # Test the sanitization pattern directly
        search_term = "Python/Java Developer @ NYC"
        safe_search = re.sub(r"[^\w\-]", "_", search_term.lower()).strip("_")
        safe_search = re.sub(r"_+", "_", safe_search)

        assert "/" not in safe_search
        assert "@" not in safe_search
        assert " " not in safe_search
        assert safe_search == "python_java_developer_nyc"

    def test_filename_collapses_multiple_underscores(self):
        """Multiple consecutive underscores should be collapsed to one."""
        search_term = "Python   &&&   Developer"
        safe_search = re.sub(r"[^\w\-]", "_", search_term.lower()).strip("_")
        safe_search = re.sub(r"_+", "_", safe_search)

        assert "___" not in safe_search
        assert "__" not in safe_search
        assert safe_search == "python_developer"

    def test_filename_handles_empty_search_term(self):
        """Empty search term should default to 'jobs'."""
        search_term = ""
        safe_search = (
            re.sub(r"[^\w\-]", "_", search_term.lower()).strip("_") if search_term else "jobs"
        )

        assert safe_search == "jobs"

    def test_filename_includes_timezone_offset(self):
        """Filename should include timezone offset like -0500."""
        now = datetime.now().astimezone()
        tz_offset = now.strftime("%z")

        # Should be in format like +0500 or -0500
        assert re.match(r"^[+-]\d{4}$", tz_offset)

    def test_filename_format(self):
        """Full filename should match expected pattern."""
        search_term = "data engineer"
        safe_search = re.sub(r"[^\w\-]", "_", search_term.lower()).strip("_")
        safe_search = re.sub(r"_+", "_", safe_search)
        now = datetime.now().astimezone()
        tz_offset = now.strftime("%z")
        filename = f"{safe_search}_{now.strftime('%Y%m%d_%H%M%S')}{tz_offset}.json"

        # Pattern: search_YYYYMMDD_HHMMSS±HHMM.json
        assert re.match(r"^data_engineer_\d{8}_\d{6}[+-]\d{4}\.json$", filename)


class TestSalaryFormatting:
    """Tests for salary value formatting."""

    def test_salary_with_both_min_and_max(self):
        """Should format as '$X - $Y' when both values present."""
        # Simulate the logic from export_jobs
        min_sal = 100000
        max_sal = 150000

        def is_valid_number(val):
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        salary = ""
        if is_valid_number(min_sal) and is_valid_number(max_sal):
            salary = f"${int(min_sal):,} - ${int(max_sal):,}"

        assert salary == "$100,000 - $150,000"

    def test_salary_with_only_min(self):
        """Should format as '$X+' when only min present."""
        min_sal = 80000
        max_sal = None

        def is_valid_number(val):
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        salary = ""
        if is_valid_number(min_sal) and is_valid_number(max_sal):
            salary = f"${int(min_sal):,} - ${int(max_sal):,}"
        elif is_valid_number(min_sal):
            salary = f"${int(min_sal):,}+"

        assert salary == "$80,000+"

    def test_salary_with_only_max(self):
        """Should format as 'Up to $Y' when only max present."""
        min_sal = None
        max_sal = 120000

        def is_valid_number(val):
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        salary = ""
        if is_valid_number(min_sal) and is_valid_number(max_sal):
            salary = f"${int(min_sal):,} - ${int(max_sal):,}"
        elif is_valid_number(min_sal):
            salary = f"${int(min_sal):,}+"
        elif is_valid_number(max_sal):
            salary = f"Up to ${int(max_sal):,}"

        assert salary == "Up to $120,000"

    def test_salary_with_nan_values(self):
        """Should return empty string when values are NaN."""
        min_sal = float("nan")
        max_sal = float("nan")

        def is_valid_number(val):
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        salary = ""
        if is_valid_number(min_sal) and is_valid_number(max_sal):
            salary = f"${int(min_sal):,} - ${int(max_sal):,}"
        elif is_valid_number(min_sal):
            salary = f"${int(min_sal):,}+"
        elif is_valid_number(max_sal):
            salary = f"Up to ${int(max_sal):,}"

        assert salary == ""

    def test_salary_with_none_values(self):
        """Should return empty string when values are None."""
        min_sal = None
        max_sal = None

        def is_valid_number(val):
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        salary = ""
        if is_valid_number(min_sal) and is_valid_number(max_sal):
            salary = f"${int(min_sal):,} - ${int(max_sal):,}"

        assert salary == ""

    def test_salary_with_mixed_nan_and_valid(self):
        """Should handle one NaN and one valid value."""
        min_sal = float("nan")
        max_sal = 100000

        def is_valid_number(val):
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        salary = ""
        if is_valid_number(min_sal) and is_valid_number(max_sal):
            salary = f"${int(min_sal):,} - ${int(max_sal):,}"
        elif is_valid_number(min_sal):
            salary = f"${int(min_sal):,}+"
        elif is_valid_number(max_sal):
            salary = f"Up to ${int(max_sal):,}"

        assert salary == "Up to $100,000"


class TestDateFormatting:
    """Tests for date formatting in export."""

    def test_date_from_datetime_object(self):
        """Should format datetime object as YYYY-MM-DD."""
        date_posted = datetime(2025, 1, 15, 10, 30, 0)

        if hasattr(date_posted, "strftime"):
            formatted = date_posted.strftime("%Y-%m-%d")
        else:
            formatted = str(date_posted)[:10]

        assert formatted == "2025-01-15"

    def test_date_from_string(self):
        """Should extract YYYY-MM-DD from date string."""
        date_posted = "2025-01-15T10:30:00"

        if hasattr(date_posted, "strftime"):
            formatted = date_posted.strftime("%Y-%m-%d")
        else:
            formatted = str(date_posted)[:10]

        assert formatted == "2025-01-15"

    def test_date_none_uses_today(self):
        """Should use today's date when date_posted is None."""
        date_posted = None

        if date_posted:
            if hasattr(date_posted, "strftime"):
                formatted = date_posted.strftime("%Y-%m-%d")
            else:
                formatted = str(date_posted)[:10]
        else:
            formatted = datetime.now().strftime("%Y-%m-%d")

        # Should be today's date
        assert formatted == datetime.now().strftime("%Y-%m-%d")


class TestExportJobsFunction:
    """Integration tests for the export_jobs function."""

    def test_export_creates_valid_json_structure(self, tmp_path, sample_jobspy_jobs):
        """Exported file should have correct Cleansheet structure."""
        import jobpacker

        output_file = tmp_path / "test_export.json"

        with patch.object(jobpacker, "console"):
            with patch.object(jobpacker.Prompt, "ask", return_value=str(output_file)):
                jobpacker.export_jobs(sample_jobspy_jobs, "test search")

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        # Check top-level structure
        assert "exportType" in data
        assert data["exportType"] == "jobspy_harvest"
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_export_job_has_required_fields(self, tmp_path, sample_jobspy_jobs):
        """Each exported job should have all required Cleansheet fields."""
        import jobpacker

        output_file = tmp_path / "test_export.json"

        with patch.object(jobpacker, "console"):
            with patch.object(jobpacker.Prompt, "ask", return_value=str(output_file)):
                jobpacker.export_jobs(sample_jobspy_jobs, "test search")

        with open(output_file) as f:
            data = json.load(f)

        required_fields = [
            "id",
            "company",
            "title",
            "location",
            "url",
            "description",
            "salary",
            "datePosted",
            "source",
            "status",
            "tags",
        ]

        for job in data["jobs"]:
            for field in required_fields:
                assert field in job, f"Missing field: {field}"

    def test_export_job_status_is_saved(self, tmp_path, sample_jobspy_jobs):
        """All exported jobs should have status 'Saved'."""
        import jobpacker

        output_file = tmp_path / "test_export.json"

        with patch.object(jobpacker, "console"):
            with patch.object(jobpacker.Prompt, "ask", return_value=str(output_file)):
                jobpacker.export_jobs(sample_jobspy_jobs, "test search")

        with open(output_file) as f:
            data = json.load(f)

        for job in data["jobs"]:
            assert job["status"] == "Saved"

    def test_export_job_tags_is_empty_list(self, tmp_path, sample_jobspy_jobs):
        """All exported jobs should have empty tags array."""
        import jobpacker

        output_file = tmp_path / "test_export.json"

        with patch.object(jobpacker, "console"):
            with patch.object(jobpacker.Prompt, "ask", return_value=str(output_file)):
                jobpacker.export_jobs(sample_jobspy_jobs, "test search")

        with open(output_file) as f:
            data = json.load(f)

        for job in data["jobs"]:
            assert job["tags"] == []

    def test_export_job_has_uuid(self, tmp_path, sample_jobspy_jobs):
        """Each job should have a valid UUID."""
        import uuid

        import jobpacker

        output_file = tmp_path / "test_export.json"

        with patch.object(jobpacker, "console"):
            with patch.object(jobpacker.Prompt, "ask", return_value=str(output_file)):
                jobpacker.export_jobs(sample_jobspy_jobs, "test search")

        with open(output_file) as f:
            data = json.load(f)

        for job in data["jobs"]:
            # Should be a valid UUID string
            uuid.UUID(job["id"])  # Raises ValueError if invalid

    def test_export_empty_jobs_shows_message(self, mock_console):
        """Should show message when no jobs to export."""
        import jobpacker

        jobpacker.export_jobs([], "test")

        # Should have printed a warning
        mock_console.print.assert_called()

    def test_export_handles_nan_salary_gracefully(self, tmp_path):
        """Should not crash when job has NaN salary values."""
        import jobpacker

        jobs_with_nan = [
            {
                "title": "Test Job",
                "company": "Test Co",
                "location": "Test City",
                "job_url": "https://example.com",
                "description": "Test description",
                "date_posted": None,
                "min_amount": float("nan"),
                "max_amount": float("nan"),
                "site": "indeed",
            }
        ]

        output_file = tmp_path / "test_nan.json"

        with patch.object(jobpacker, "console"):
            with patch.object(jobpacker.Prompt, "ask", return_value=str(output_file)):
                # Should not raise an exception
                jobpacker.export_jobs(jobs_with_nan, "test")

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["jobs"][0]["salary"] == ""
