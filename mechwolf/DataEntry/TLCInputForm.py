import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import List

class TLCInputForm:
    """
    A class to create and manage a TLC (Thin Layer Chromatography) input form using ipywidgets.
    The form allows users to input the number of spots, their identities, and distances from the baseline.
    It also includes functionality to calculate and display the Rf values based on the input data.
    Methods:
        __init__:
            Initializes the TLCInputForm instance and creates the initial widgets.
        create_initial_widgets:
            Creates the initial form for entering the number of spots and a button to create the detailed form.
        on_create_form:
            Handles the creation of the detailed form based on the number of spots entered.
            It includes input fields for spot identities and distances, as well as a solvent distance input.
            Also includes a button to calculate Rf values and display the results.
    Args:
        None
    Returns:
        None
    """

    def __init__(self) -> None:
        self.main_output: widgets.Output = widgets.Output()
        self.spots_box: widgets.VBox
        with self.main_output:
            self.create_initial_widgets()

    def create_initial_widgets(self) -> None:
        # Initial form for number of spots
        spots_box: widgets.VBox = widgets.VBox(
            [
                widgets.Label("Number of spots:"),
                widgets.IntText(min=1, layout=widgets.Layout(width="200px")),
                widgets.Button(description="Create Form"),
            ]
        )

        spots_box.children[2].on_click(self.on_create_form)
        self.spots_box = spots_box
        display(spots_box)

    def on_create_form(self, b: widgets.Button) -> None:
        try:
            num_spots: int = self.spots_box.children[1].value
            if num_spots <= 0:
                raise ValueError("Please enter a positive number")

            # Use wait parameter for compatibility across versions
            clear_output(wait=True)

            # Create headers with bigger font and bold styling
            # Use HTML styling that works in both v6 and v7
            headers: widgets.HBox = widgets.HBox(
                [
                    widgets.HTML(
                        value='<div style="font-size: 16px; font-weight: bold; margin: 0;">Identity of spot</div>',
                        layout=widgets.Layout(width="200px"),
                    ),
                    widgets.HTML(
                        value='<div style="font-size: 16px; font-weight: bold; margin: 0;">Distance from baseline (cm)</div>',
                        layout=widgets.Layout(width="200px"),
                    ),
                ],
                layout=widgets.Layout(
                    justify_content="space-between", width="500px", margin="5px 0"
                ),
            )

            # Create input boxes for samples
            inputs: List[widgets.HBox] = []
            for i in range(num_spots):
                sample_name: widgets.Text = widgets.Text(
                    placeholder=f"Spot {i+1}", layout=widgets.Layout(width="200px")
                )
                sample_distance: widgets.FloatText = widgets.FloatText(
                    layout=widgets.Layout(width="200px")
                )
                inputs.append(
                    widgets.HBox(
                        [sample_name, sample_distance],
                        layout=widgets.Layout(
                            justify_content="space-between", width="500px"
                        ),
                    )
                )

            # Add solvent distance input with matching header style and spacing
            solvent_distance: widgets.VBox = widgets.VBox(
                [
                    widgets.HTML(
                        value='<div style="font-size: 16px; font-weight: bold; margin: 5px 0;">Distance travelled by solvent front (cm)</div>',
                        layout=widgets.Layout(width="300px"),
                    ),
                    widgets.FloatText(layout=widgets.Layout(width="200px")),
                ],
                layout=widgets.Layout(margin="10px 0 20px 0"),
            )  # Add top margin for spacing

            calc_button: widgets.Button = widgets.Button(
                description="Calculate Rf Values",
                button_style="success",
                style={"button_color": "#007F5F", "font_color": "black"},
            )

            result_output: widgets.Output = widgets.Output()

            def on_calculate(b: widgets.Button) -> None:
                with result_output:
                    clear_output(wait=True)
                    try:
                        solvent_dist: float = solvent_distance.children[1].value
                        if solvent_dist == 0:
                            raise ValueError("Solvent distance cannot be zero")

                        for i in range(num_spots):
                            sample_name: str = (
                                inputs[i].children[0].value or f"Spot {i+1}"
                            )
                            sample_dist: float = inputs[i].children[1].value
                            rf: float = round(sample_dist / solvent_dist, 4)
                            print(f"RF value for {sample_name}: {rf}")
                    except Exception as e:
                        print(f"Error: {e}")

            calc_button.on_click(on_calculate)

            # Use a slightly different display approach for v7
            form_container = widgets.VBox(
                [
                    headers,
                    widgets.VBox(inputs),
                    solvent_distance,
                    calc_button,
                    result_output,
                ]
            )
            
            # Make sure display works properly in both versions
            display(form_container)

        except Exception as e:
            print(f"Error: {e}")


def create_tlc_form() -> TLCInputForm:
    return TLCInputForm()


if __name__ == "__main__":
    create_tlc_form()
