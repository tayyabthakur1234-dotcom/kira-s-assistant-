from plugins.manager import plugin_manager
from plugins.default_plugins.dev_plugins import GitHubPlugin, GitPlugin, VSCodePlugin, DockerPlugin
from plugins.default_plugins.google_plugins import (
    GoogleDrivePlugin, GoogleCalendarPlugin, GoogleDocsPlugin,
    GoogleSheetsPlugin, GmailPlugin, MapsPlugin
)
from plugins.default_plugins.messaging_plugins import (
    TelegramPlugin, DiscordPlugin, SlackPlugin, WhatsAppPlugin
)
from plugins.default_plugins.media_plugins import (
    SpotifyPlugin, YouTubePlugin, OBSStudioPlugin, NotionPlugin,
    SteamPlugin, WindowsSettingsPlugin, WeatherPlugin, NewsPlugin
)

def register_all_default_plugins():
    """Instantiates and registers all Phase 6 default plugins into plugin_manager."""
    plugins = [
        GitHubPlugin(), GitPlugin(), VSCodePlugin(), DockerPlugin(),
        GoogleDrivePlugin(), GoogleCalendarPlugin(), GoogleDocsPlugin(),
        GoogleSheetsPlugin(), GmailPlugin(), MapsPlugin(),
        TelegramPlugin(), DiscordPlugin(), SlackPlugin(), WhatsAppPlugin(),
        SpotifyPlugin(), YouTubePlugin(), OBSStudioPlugin(), NotionPlugin(),
        SteamPlugin(), WindowsSettingsPlugin(), WeatherPlugin(), NewsPlugin()
    ]
    for p in plugins:
        plugin_manager.register_plugin(p)

# Auto register on package import
register_all_default_plugins()
