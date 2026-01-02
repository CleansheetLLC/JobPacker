"""Tests for UI and menu functions."""

from unittest.mock import MagicMock, patch


class TestDisplayBanner:
    """Tests for display_banner function."""

    def test_display_banner_prints_panel(self, mock_console):
        """Should print a Panel with the banner."""
        import jobpacker

        jobpacker.display_banner()

        # Should have called console.print with a Panel
        mock_console.print.assert_called_once()


class TestDisplayMainMenu:
    """Tests for display_main_menu function."""

    def test_main_menu_returns_valid_choice(self, mock_console):
        """Should return user's menu choice."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", return_value="1"):
            choice = jobpacker.display_main_menu()

        assert choice == "1"

    def test_main_menu_shows_four_options(self, mock_console):
        """Should display all four menu options."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", return_value="1"):
            jobpacker.display_main_menu()

        # Check that console.print was called multiple times for menu items
        assert mock_console.print.call_count >= 4


class TestDisplaySettingsMenu:
    """Tests for display_settings_menu function."""

    def test_settings_menu_returns_on_zero(self, mock_console, default_config):
        """Should return config when user selects 0 (back)."""
        import jobpacker

        with patch.object(jobpacker.Prompt, "ask", return_value="0"):
            with patch.object(jobpacker, "save_config"):
                result = jobpacker.display_settings_menu(default_config.copy())

        assert result is not None

    def test_settings_menu_updates_default_search(self, mock_console, default_config):
        """Should update default_search when option 1 selected."""
        import jobpacker

        config = default_config.copy()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["1", "new search", "0"]):
            with patch.object(jobpacker, "save_config"):
                result = jobpacker.display_settings_menu(config)

        assert result["default_search"] == "new search"

    def test_settings_menu_updates_default_location(self, mock_console, default_config):
        """Should update default_location when option 2 selected."""
        import jobpacker

        config = default_config.copy()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["2", "New York", "0"]):
            with patch.object(jobpacker, "save_config"):
                result = jobpacker.display_settings_menu(config)

        assert result["default_location"] == "New York"

    def test_settings_menu_updates_results_per_site(self, mock_console, default_config):
        """Should update results_per_site when option 3 selected."""
        import jobpacker

        config = default_config.copy()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["3", "0"]):
            with patch.object(jobpacker.IntPrompt, "ask", return_value=50):
                with patch.object(jobpacker, "save_config"):
                    result = jobpacker.display_settings_menu(config)

        assert result["results_per_site"] == 50

    def test_settings_menu_updates_remote_only(self, mock_console, default_config):
        """Should update remote_only when option 4 selected."""
        import jobpacker

        config = default_config.copy()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["4", "0"]):
            with patch.object(jobpacker.Confirm, "ask", return_value=True):
                with patch.object(jobpacker, "save_config"):
                    result = jobpacker.display_settings_menu(config)

        assert result["remote_only"] is True

    def test_settings_menu_updates_job_type(self, mock_console, default_config):
        """Should update job_type when option 5 selected."""
        import jobpacker

        config = default_config.copy()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["5", "fulltime", "0"]):
            with patch.object(jobpacker, "save_config"):
                result = jobpacker.display_settings_menu(config)

        assert result["job_type"] == "fulltime"

    def test_settings_menu_updates_job_boards(self, mock_console, default_config):
        """Should update job_boards when option 6 selected."""
        import jobpacker

        config = default_config.copy()

        with patch.object(jobpacker.Prompt, "ask", side_effect=["6", "1,2", "0"]):
            with patch.object(jobpacker, "save_config"):
                result = jobpacker.display_settings_menu(config)

        assert result["job_boards"] == ["indeed", "linkedin"]

    def test_settings_menu_saves_on_exit(self, mock_console, default_config):
        """Should call save_config when exiting."""
        import jobpacker

        config = default_config.copy()
        mock_save = MagicMock()

        with patch.object(jobpacker.Prompt, "ask", return_value="0"):
            with patch.object(jobpacker, "save_config", mock_save):
                jobpacker.display_settings_menu(config)

        mock_save.assert_called_once_with(config)


class TestMainLoop:
    """Tests for main application loop."""

    def test_main_exits_on_option_4(self, mock_console):
        """Should exit when user selects option 4."""
        import jobpacker

        with patch.object(jobpacker, "display_banner"):
            with patch.object(jobpacker, "load_config", return_value={}):
                with patch.object(jobpacker, "display_main_menu", return_value="4"):
                    jobpacker.main()

        # Should have printed goodbye
        mock_console.print.assert_called()

    def test_main_calls_search_on_option_1(self, mock_console):
        """Should call search_jobs when user selects option 1."""
        import jobpacker

        mock_search = MagicMock(return_value=([], ""))

        with patch.object(jobpacker, "display_banner"):
            with patch.object(jobpacker, "load_config", return_value={}):
                with patch.object(jobpacker, "display_main_menu", side_effect=["1", "4"]):
                    with patch.object(jobpacker, "search_jobs", mock_search):
                        jobpacker.main()

        mock_search.assert_called_once()

    def test_main_calls_settings_on_option_2(self, mock_console):
        """Should call display_settings_menu when user selects option 2."""
        import jobpacker

        mock_settings = MagicMock(return_value={})

        with patch.object(jobpacker, "display_banner"):
            with patch.object(jobpacker, "load_config", return_value={}):
                with patch.object(jobpacker, "display_main_menu", side_effect=["2", "4"]):
                    with patch.object(jobpacker, "display_settings_menu", mock_settings):
                        jobpacker.main()

        mock_settings.assert_called_once()

    def test_main_calls_export_on_option_3(self, mock_console):
        """Should call export_jobs when user selects option 3."""
        import jobpacker

        mock_export = MagicMock()

        with patch.object(jobpacker, "display_banner"):
            with patch.object(jobpacker, "load_config", return_value={}):
                with patch.object(jobpacker, "display_main_menu", side_effect=["3", "4"]):
                    with patch.object(jobpacker, "export_jobs", mock_export):
                        jobpacker.main()

        mock_export.assert_called_once()

    def test_main_passes_jobs_to_export(self, mock_console):
        """Should pass search results to export_jobs."""
        import jobpacker

        test_jobs = [{"title": "Test Job"}]
        mock_search = MagicMock(return_value=(test_jobs, "test"))
        mock_export = MagicMock()

        with patch.object(jobpacker, "display_banner"):
            with patch.object(jobpacker, "load_config", return_value={}):
                with patch.object(jobpacker, "display_main_menu", side_effect=["1", "3", "4"]):
                    with patch.object(jobpacker, "search_jobs", mock_search):
                        with patch.object(jobpacker, "export_jobs", mock_export):
                            jobpacker.main()

        # Export should be called with the jobs from search
        mock_export.assert_called_once_with(test_jobs, "test")
