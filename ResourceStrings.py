"""
All the strings displayed to the user should be stored here. This way it is easier to change wording / spelling. It is also nice if it'll ever get translated.
"""

program_title = "Categories exporter"

exporter_instruction = \
        ("INSTRUCTION:\n"
         " Select backup to copy sharedconfig.vdf to a safe location.\n"
         " Select retore to copy it back to steam. Current sharedconfig.vdf would be renamed (no files are deleted).\n"
         " Select export to read it in an easy-to-read format.")

selector_instruction = \
    ("INSTRUCTION:\n"
     " Select the steam users you want to backup / export.\n"
     " If your user isn't listed on the box bellow you can add it by browsing to:\n"
     " Steam\\userdata\\<USER_ID>\\7\\remote\\sharedconfig.vdf")


exporter_button_backup = "Backup"
exporter_button_restore = "Restore"
exporter_button_export = "Export"
selector_button_select = "Select"
selector_button_browse = "Browse"
exporter_checkbox_legal = "Hide © and ™"
exporter_text_prefix = "Selected Steam Location:\n"

exporter_title_backup = "Save backup to.."
exporter_title_restore = "Restore backup from.."
exporter_title_export = "Export to.."
selector_title_browse = "Select sharecondig.vdf.."

text_file = "Text file"
vdf_file = "Valve's Data Format"
all_file = "all files"



sharedconfigvdf = "sharedconfig.vdf"




error_backup = "Backup Error"
error_backup_text_same = "Backup error: Source and target file are the same"
error_backup_text_not_vdf = "Backup error: The source file is probably not sharedconfig.vdf"
error_restore = "Restore Error"
error_restore_text_same = "Restore error: Source and target file are the same"
error_restore_text_not_vdf = "Restore error: The source file is probably not sharedconfig.vdf"


