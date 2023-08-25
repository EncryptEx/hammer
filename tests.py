# unit test

import json
import unittest
from os import listdir
from os.path import isfile, join


def jsonToDict(filename):
    with open(filename) as f_in:
        return json.load(f_in)


jsonRequiredLines = [
    "help_description",
    "help_moderation_title",
    "user",
    "reason",
    "help_automod_title",
    "help_automod_description",
    "help_chatmod_title",
    "help_chatmod_description",
    "help_various_title",
    "help_various_description",
    "help_links_title",
    "help_links_description",
    "help_commands_title",
    "help_commands_description",
    "footer_executed_by",
    "hello_command",
    "error_deliver_msg",
    "automod_warn_title",
    "automod_warn_description",
    "automod_warn_footer",
    "automod_warn_reason",
    "automod_count_title",
    "automod_count_description",
    "automod_removed_title",
    "automod_removed_description",
    "automod_nothappy_title",
    "automod_nothappy_description",
    "error_404",
    "error_403",
    "whois_title",
    "whois_description",
    "error_self_ban",
    "punishment_default_reason",
    "unpunishment_default_reason",
    "ban_msg",
    "ban_title",
    "ban_description",
    "error_ban_perm",
    "error_self_kick",
    "kick_msg",
    "error_kick_perm",
    "kick_title",
    "kick_description",
    "error_self_warn",
    "warn_msg",
    "warn_title",
    "warn_description",
    "warn_no_warns",
    "seewarns_title",
    "unwarn_no_warns",
    "unwarn_description_msg",
    "unwarn_wrong_selection",
    "unwarn_msg",
    "unwarn_title",
    "unwarn_description",
    "unwarn_count_with_success",
    "plural_warn",
    "singular_warn",
    "clearwarns_msg",
    "clearwarns_description",
    "clearwarns_title",
    "error_automod_syntax",
    "automod_success_action",
    "error_automod",
    "modified",
    "removed",
    "setdelay_title",
    "for",
    "setdelay_description",
    "mute_title",
    "mute_description",
    "mute_msg",
    "unmute_msg",
    "unmute_title",
    "unmute_description",
    "lock_title",
    "lock_description",
    "unlock_title",
    "unlock_description",
    "suggest_success",
    "hammer_invite",
    "hammer_link",
    "enabled",
    "disabled",
    "settings_module",
    "error_settings_syntax",
    "settings_title",
    "settings_description",
    "settings_enable_automod",
    "settings_disable_automod",
    "settings_status",
    "help_language_title",
    "warns_line_loop",
    "seewarns_chart_title",
]


class HammerTest(unittest.TestCase):
    def test_lanugages(self):
        langFiles = [f for f in listdir("./langs") if isfile(join("./langs", f))]
        for languageFile in langFiles:
            filename = languageFile.split(".")[0]
            dictionary = jsonToDict("./langs/" + languageFile)
            self.assertEqual(
                len(dictionary.items()),
                len(jsonRequiredLines),
                "There's a missing line in the language json file: " + filename,
            )
            for k, v in dictionary.items():
                self.assertTrue(
                    k in jsonRequiredLines,
                    "The line " + k + " is wrong spelled " + languageFile,
                )


if __name__ == "__main__":
    unittest.main()
