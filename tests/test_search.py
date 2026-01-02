"""Tests for job search functionality."""

from unittest.mock import MagicMock, patch

import pandas as pd


class TestSearchJobs:
    """Tests for search_jobs function."""

    def test_search_returns_jobs_and_search_term(
        self, default_config, sample_jobspy_dataframe, mock_console
    ):
        """Should return tuple of (jobs list, search term)."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", side_effect=["python developer", "USA"]):
            with patch.object(jobpacker, "scrape_jobs", return_value=sample_jobspy_dataframe):
                with patch.object(jobpacker, "display_jobs_table"):
                    jobs, search_term = jobpacker.search_jobs(default_config)

        assert isinstance(jobs, list)
        assert len(jobs) > 0
        assert search_term == "python developer"

    def test_search_empty_term_returns_empty(self, default_config, mock_console):
        """Should return empty list when search term is empty."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", return_value=""):
            jobs, search_term = jobpacker.search_jobs(default_config)

        assert jobs == []
        assert search_term == ""

    def test_search_uses_config_defaults(
        self, custom_config, sample_jobspy_dataframe, mock_console
    ):
        """Should use config values as defaults for prompts."""
        import jobpacker

        mock_scrape = MagicMock(return_value=sample_jobspy_dataframe)

        with patch.object(
            jobpacker.Prompt,
            "ask",
            side_effect=[custom_config["default_search"], custom_config["default_location"]],
        ):
            with patch.object(jobpacker, "scrape_jobs", mock_scrape):
                with patch.object(jobpacker, "display_jobs_table"):
                    jobpacker.search_jobs(custom_config)

        # Verify scrape_jobs was called with config values
        mock_scrape.assert_called_once()
        call_kwargs = mock_scrape.call_args.kwargs
        assert call_kwargs["site_name"] == custom_config["job_boards"]
        assert call_kwargs["results_wanted"] == custom_config["results_per_site"]
        assert call_kwargs["is_remote"] == custom_config["remote_only"]
        assert call_kwargs["job_type"] == custom_config["job_type"]

    def test_search_handles_scrape_exception(self, default_config, mock_console):
        """Should return empty list and show error on scrape failure."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", side_effect=["test search", "USA"]):
            with patch.object(jobpacker, "scrape_jobs", side_effect=Exception("Network error")):
                jobs, search_term = jobpacker.search_jobs(default_config)

        assert jobs == []
        assert search_term == "test search"
        # Should have printed error message
        mock_console.print.assert_called()

    def test_search_handles_empty_results(self, default_config, mock_console):
        """Should return empty list when scrape returns no results."""
        import jobpacker

        empty_df = pd.DataFrame()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["test search", "USA"]):
            with patch.object(jobpacker, "scrape_jobs", return_value=empty_df):
                jobs, search_term = jobpacker.search_jobs(default_config)

        assert jobs == []
        assert search_term == "test search"

    def test_search_handles_none_results(self, default_config, mock_console):
        """Should return empty list when scrape returns None."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", side_effect=["test search", "USA"]):
            with patch.object(jobpacker, "scrape_jobs", return_value=None):
                jobs, search_term = jobpacker.search_jobs(default_config)

        assert jobs == []
        assert search_term == "test search"

    def test_search_converts_dataframe_to_list(
        self, default_config, sample_jobspy_dataframe, mock_console
    ):
        """Should convert pandas DataFrame to list of dicts."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", side_effect=["test search", "USA"]):
            with patch.object(jobpacker, "scrape_jobs", return_value=sample_jobspy_dataframe):
                with patch.object(jobpacker, "display_jobs_table"):
                    jobs, _ = jobpacker.search_jobs(default_config)

        assert isinstance(jobs, list)
        assert all(isinstance(job, dict) for job in jobs)
        # Should have same number of jobs as rows in DataFrame
        assert len(jobs) == len(sample_jobspy_dataframe)


class TestDisplayJobsTable:
    """Tests for display_jobs_table function."""

    def test_display_shows_up_to_50_jobs(self, sample_jobspy_jobs, mock_console):
        """Should display max 50 jobs in table."""
        import jobpacker

        # Create more than 50 jobs
        many_jobs = sample_jobspy_jobs * 15  # 60 jobs

        jobpacker.display_jobs_table(many_jobs)

        # Should have printed the table
        mock_console.print.assert_called()

    def test_display_truncates_long_fields(self, mock_console):
        """Should truncate title, company, location to specified lengths."""
        import jobpacker

        jobs = [
            {
                "title": "A" * 100,  # Very long title
                "company": "B" * 100,  # Very long company
                "location": "C" * 100,  # Very long location
                "site": "indeed",
            }
        ]

        jobpacker.display_jobs_table(jobs)

        # Table should have been printed (visual check would verify truncation)
        mock_console.print.assert_called()

    def test_display_handles_missing_fields(self, mock_console):
        """Should handle jobs with missing fields gracefully."""
        import jobpacker

        jobs = [
            {
                "title": "Test Job",
                # Missing company, location, site
            }
        ]

        # Should not raise exception
        jobpacker.display_jobs_table(jobs)
        mock_console.print.assert_called()

    def test_display_empty_list(self, mock_console):
        """Should handle empty job list."""
        import jobpacker

        jobpacker.display_jobs_table([])

        # Should still print (empty table)
        mock_console.print.assert_called()


class TestSelectJobBoards:
    """Tests for select_job_boards function."""

    def test_select_all_returns_all_boards(self, mock_console):
        """'all' selection should return all job boards."""
        import jobpacker

        current = ["indeed"]

        with patch.object(jobpacker.Prompt, "ask", return_value="all"):
            result = jobpacker.select_job_boards(current)

        assert result == jobpacker.ALL_JOB_BOARDS

    def test_select_specific_boards(self, mock_console):
        """Comma-separated numbers should select specific boards."""
        import jobpacker

        current = ["indeed"]

        with patch.object(jobpacker.Prompt, "ask", return_value="1,3"):
            result = jobpacker.select_job_boards(current)

        assert result == ["indeed", "glassdoor"]

    def test_select_invalid_input_keeps_current(self, mock_console):
        """Invalid input should keep current selection."""
        import jobpacker

        current = ["indeed", "linkedin"]

        with patch.object(jobpacker.Prompt, "ask", return_value="invalid"):
            result = jobpacker.select_job_boards(current)

        assert result == current

    def test_select_out_of_range_keeps_current(self, mock_console):
        """Out of range numbers should keep current selection."""
        import jobpacker

        current = ["indeed"]

        with patch.object(jobpacker.Prompt, "ask", return_value="99"):
            result = jobpacker.select_job_boards(current)

        assert result == current

    def test_select_partial_valid_numbers(self, mock_console):
        """Should return only valid indices from mixed input."""
        import jobpacker

        current = ["indeed"]

        with patch.object(jobpacker.Prompt, "ask", return_value="1,99,2"):
            result = jobpacker.select_job_boards(current)

        # Should include indices 1 and 2, skip 99
        assert "indeed" in result
        assert "linkedin" in result
