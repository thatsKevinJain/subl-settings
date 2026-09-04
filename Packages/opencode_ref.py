import os
import sublime
import sublime_plugin


def _rel_from_folders(abs_path, window):
    if not abs_path:
        return None
    for folder in window.folders():
        try:
            rel = os.path.relpath(abs_path, folder)
        except ValueError:
            continue
        if not rel.startswith(".."):
            return rel.replace(os.sep, "/")
    return None


def _ranges_from_selection(view, sel):
    lines = []
    for region in sel:
        if region.empty():
            row, _ = view.rowcol(region.begin())
            lines.append((row + 1, row + 1))
        else:
            begin_row, _ = view.rowcol(region.begin())
            end_row, _ = view.rowcol(region.end() - 1)
            lines.append((begin_row + 1, end_row + 1))
    return lines


class opencodeCopyReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if not view or not view.file_name():
            sublime.status_message("opencode: no file in active view")
            return
        rel = _rel_from_folders(view.file_name(), self.window)
        if not rel:
            sublime.status_message("opencode: file is outside open folders")
            return
        sel = view.sel()
        if not sel:
            sublime.status_message("opencode: no selection")
            return
        ranges = _ranges_from_selection(view, sel)
        refs = []
        for start, end in ranges:
            if start == end:
                refs.append(f"@{rel}#L{start}")
            else:
                refs.append(f"@{rel}#L{start}-{end}")
        ref_str = " ".join(refs)
        sublime.set_clipboard(ref_str)
        preview = ref_str if len(ref_str) <= 80 else ref_str[:77] + "..."
        sublime.status_message(f"Copied: {preview}")
