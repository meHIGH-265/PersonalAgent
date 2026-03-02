from unittest.mock import Mock, patch

from src.Agents.Tools.ToolManager import MyToolManager


class TestToolHostAndPort:
    def test_set_tool_host(self):
        MyToolManager.set_tool_host("localhost")
        assert MyToolManager.get_tool_host() == "localhost"

    def test_set_tool_port(self):
        MyToolManager.set_tool_port(8080)
        assert MyToolManager.get_tool_port() == 8080


class TestSendPostRequestForTool:
    @patch("src.Agents.Brain.Tools.BaseTools.requests.post")
    @patch("src.Agents.Brain.Tools.BaseTools.MyLogger.log")
    def test_successful_post_request(self, mock_log, mock_post):
        MyToolManager.set_tool_host("localhost")
        MyToolManager.set_tool_port(1234)

        mock_response = Mock()
        mock_response.text = "ok"
        mock_post.return_value = mock_response

        result = MyToolManager.send_post_request_for_tool(
            tool_name="test_tool",
            json_data={"x": "1"},
        )

        assert result == "ok"

        mock_post.assert_called_once()
        mock_log.assert_called()  # logging side effect occurred

    @patch("src.Agents.Brain.Tools.BaseTools.requests.post", side_effect=Exception)
    @patch("src.Agents.Brain.Tools.BaseTools.MyLogger.log")
    def test_post_request_exception_returns_error_message(self, mock_log, mock_post):
        result = MyToolManager.send_post_request_for_tool(
            tool_name="test_tool",
            json_data={"x": "1"},
        )

        assert "Tool is unuseable for the moment" in result


class TestGetBaseToolsByName:
    def test_returns_all_tools_when_names_is_none(self):
        result = MyToolManager.get_base_tools_by_name()

        assert result == MyToolManager.tools

    def test_returns_only_requested_tools(self):
        result = MyToolManager.get_base_tools_by_name(["create_file", "list_files"])

        assert set(result.keys()) == {"create_file", "list_files"}
