from __future__ import annotations
from typing import TYPE_CHECKING, Any

import sublime

from ..import ui
from ..import dap

from .import css
from .tabbed import TabbedView

if TYPE_CHECKING:
	from ..debugger import Debugger


class ModulesTabbedView(TabbedView):
	def __init__(self, debugger: Debugger):
		super().__init__('Modules')
		self.debugger = debugger
		self.expanded: dict[Any, bool] = {}
		self._visible = False

		self.debugger.on_session_modules_updated.add(self.updated)
		self.debugger.on_session_removed.add(self.updated)

	def visible(self) -> bool:
		return self._visible

	def updated(self, session: dap.Session):
		self._visible = False
		for session in self.debugger.sessions:
			if session.modules:
				self._visible = True
				break

		self.dirty_header()
		self.dirty()

	def is_expanded(self, module: dap.Module):
		return self.expanded.get(module.id, False)

	def toggle_expanded(self, module: dap.Module):
		if self.is_expanded(module):
			self.expanded[module.id] = False
		else:
			self.expanded[module.id] = True

		self.dirty()

	def render(self):
		items: list[ui.div] = []
		for session in self.debugger.sessions:
			items.append(ui.div(height=css.row_height)[
				ui.text(session.name)
			])

			for module in session.modules.values():
				is_expanded = self.is_expanded(module)
				image_toggle = ui.Images.shared.open if is_expanded else ui.Images.shared.close
				item = ui.div(height=css.row_height) [
					ui.icon(image_toggle, on_click=lambda module=module: self.toggle_expanded(module)),
					ui.text(module.name)
				]
				items.append(item)
				if is_expanded:
					body: list[ui.div] = []
					def add_item(label: str, value: Any):
						if value is None:
							return

						def copy():
							ui.InputList(value)[
								ui.InputListItem(lambda: sublime.set_clipboard(value), "Copy")
							].run()

						value_str = str(value)
						body.append(
							ui.div(height=3)[
								ui.span(on_click=copy)[
									ui.text(label, css=css.label_secondary),
									ui.spacer(1),
									ui.text(value_str, css=css.label),
								]
							]
						)

					add_item('version', module.version)
					add_item('optimized', module.isOptimized)
					add_item('path', module.path)
					add_item('symbols', module.symbolStatus)
					add_item('symbol file path', module.symbolFilePath)
					add_item('load address', module.addressRange)

					items.append(ui.div(css=css.table_inset)[
						body
					])

		return items
