from ...typecheck import *
from ...import core
from ...import ui

from ..import dap
from ..terminals import Terminal

from .import css

import os

class ProblemsView (ui.div):
	def __init__(self, terminal: Terminal, on_clicked_source: Callable[[dap.SourceLocation], None]) -> None:
		super().__init__(css=css.padding_left)
		self.terminal = terminal
		self.terminal.on_problems_updated.add(self.on_problems_updated)
		self.start_line = 0
		self.on_clicked_source = on_clicked_source
		self.timer = ui.Timer(self.on_tick, 0.5, True)
		self.tick = 0

	def on_problems_updated(self):
		self.dirty()

	def on_tick(self):
		# cancel the timer when we are done. People may leave this view up indefinitely and we don't want to constantly render it
		if self.terminal.finished:
			self.timer.dispose()

		self.tick += 1
		self.dirty()

	def render(self):
		items = []

		if not self.terminal.finished:
			items.append(ui.div(height=css.row_height)[
				ui.text('•' * (self.tick % 4 + 1), css=css.label_secondary)
			])
		else:
			items.append(ui.div(height=css.row_height)[
				ui.text(self.terminal.status or '[Finished]')
			])

		for file, problems in self.terminal.problems_per_file.items():
			file_rel = os.path.relpath(file, self.terminal.cwd)

			items.append(ui.div(height=css.row_height)[
				ui.click(lambda source=problems[0].source: self.on_clicked_source(source)) [
					ui.align()[
						ui.text(file_rel, css=css.label_secondary)
					]
				]
			])

			for problem in problems:
				item = ui.div(height=css.row_height, css=css.icon_sized_spacer)[
					ui.click(lambda source=problem.source: self.on_clicked_source(source))[
						ui.align()[
							ui.span(css=css.button)[
								ui.text('error', css=css.label_redish)
							],
							ui.spacer(1),
							ui.text(problem.message, css=css.label)
						]
					]
				]
				items.append(item)


		return items
