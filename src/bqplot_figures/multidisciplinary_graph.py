from typing import Any, Dict, List, Tuple, Optional

from bqplot import Figure, Bars, Axis, LinearScale, OrdinalScale
from bqplot_figures.base_graph import BaseGraph

from utils import generate_pastel_palette
from bqplot_figures.utils.multidisciplinary_graph_utils import (
    BARS_NAMES,
    get_y_consumption_bars,
    get_y_budget_bars
)




def get_multidisciplinary_graphs_y_scales(processes_data: List[Dict[str, Any]]) -> Tuple[float, float]:
    """
    Get the minimal and maximal values of all the y-scales for the budget and consumption bars from multiple processes data.

    #### Arguments :
    - `processes_data (List[Dict[str, Any]])` : A list of processes data from AéroMAPS.

    #### Returns :
    - `Tuple[float]` : A tuple containing the minimal and maximal values of all the y-scales for the budget and consumption bars.
    """
    # Get the y-values for the budget and consumption bars from all processes data :
    all_y_lines = []
    for process_data in processes_data:
        # Get the y-values for the budget bars :
        y_budget_bars = get_y_budget_bars(process_data)
        all_y_lines.extend(y_budget_bars)

        # Get the y-values for the consumption bars :
        y_consumption_bars = get_y_consumption_bars(process_data)
        all_y_lines.extend(y_consumption_bars)

    return (min(all_y_lines), max(all_y_lines)) if all_y_lines else (0.0, 0.0)


class MultidisciplinaryGraph(BaseGraph):
    """
    Graph class for displaying multidisciplinary assessment data.

    Implements the `draw()`, `update()` and `get_legend_elements()` methods.

    #### Arguments :
    - `figure_title (str)` : Title of the figure.
    - `color_palette (Optional[List[str]])` : Optional list of **2** colors for the graph. The color order applies the following logic :
        - Index 0 : Color for the budget bars.
        - Index 1 : Color for the consumption bars.
    """
    def __init__(
            self,
            figure_title: str,
            color_palette: Optional[List[str]] = None
            ) -> None:
        super().__init__()

        self.figure_title = figure_title
        self.color_palette = color_palette if color_palette is not None else generate_pastel_palette(2)

        # Placeholders for marks :
        self._bars: Bars = None


    def draw(
            self,
            process_data: Dict[str, Any],
            y_scale: LinearScale = None,
            override: bool = False,
            display_default_legend: bool = True
        ) -> Figure:
        """
        create **initial** figure with the budget and consumption bars.

        If the figure is already drawn and you just want to update the data, it is recommended to use the `update()` method instead.
        This method will not redraw the figure but will update the lines' data only.

        However, if you want to redraw the figure completely, you can set `override = True` to force a redraw.
        This action takes more time and resources to execute.

        #### Arguments :
        - `process_data (Dict[str, Any])` : The process data containing the necessary information to create the figure.
        - `y_scale (LinearScale)` : Optional scale for the y-axis. If not provided, a default scale will be created.
        - `override (bool)` : If set to `True`, the method will redraw the figure even if it is already drawn. Defaults to `False`.
        - `display_default_legend (bool)` : If set to `True`, the default legend will be displayed. Defaults to `True`.

        #### Returns :
        - `Figure` : The created or updated figure with the budget and consumption bars.
        """
        # Check is the figure is already drawn and if override is set to False :
        super().draw(process_data, override)

        # Create scales and axes :
        x_scale = OrdinalScale()
        y_scale = y_scale or LinearScale()
        x_axis = Axis(
            scale = x_scale,
            label = "Catégories",
            label_offset = "40px"
        )
        y_axis = Axis(
            scale = y_scale,
            tick_format = "0.2f",
            orientation = "vertical",
            label = "Part du budget mondial (en %)",
            label_offset = "40px"
        )

        # Plot the consumptions and budgets bars :
        y_consumption_bars = get_y_consumption_bars(process_data)
        y_budget_bars      = get_y_budget_bars(process_data)

        self._bars = Bars(
            x = BARS_NAMES,
            y = [y_consumption_bars, y_budget_bars],
            type = "grouped",
            colors = [self.color_palette[1], self.color_palette[0]],
            opacities = [0.5] * len(self.color_palette),
            labels = ["Consommations", "Budgets"],
            display_legend = display_default_legend,
            padding = 0.1,
            scales = {"x": x_scale, "y": y_scale},
        )

        # Create the figure with all marks, axes and the legend :
        self.figure = Figure(
            marks = [self._bars],
            axes = [x_axis, y_axis],
            title = self.figure_title,
            animation_duration = 1000,
            legend_location = "top-right",
            legend_style = {"stroke-width": 0}
        )

        return self.figure


    def update(self, process_data: Dict[str, Any]) -> Figure:
        # Check if the figure is already drawn :
        super().update(process_data)

        # Update the figure :
        with self.figure.hold_sync():
            # Update the y-axis of the budget and consumption bars :
            self._bars.y = [
                get_y_consumption_bars(process_data),
                get_y_budget_bars(process_data)
            ]

        return self.figure


    def get_legend_elements(self) -> Tuple[List[str], List[str], List[str]]:
        # Check if the figure is already drawn :
        super().get_legend_elements()

        # Get the legend elements :
        colors    = self._bars.colors
        labels    = self._bars.labels
        opacities = self._bars.opacities

        return colors, labels, opacities
