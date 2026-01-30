from tkinter import Menu


def _noop():
    pass


def create_menu(master, callbacks=None):
    """Create the application menu bar and return it.

    callbacks: dict mapping expected names to callables.
    Expected keys: open_settings, on_closing, open_measure, open_parameter,
    open_adjust, open_sinus, open_tunnel, open_tunnel_simulate,
    open_measure_simulate, show_simulation_info
    """
    if callbacks is None:
        callbacks = {}

    def cb(name):
        return callbacks.get(name, _noop)

    menu_bar = Menu(master)
    master.config(menu=menu_bar)

    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    # file_menu.add_separator()
    file_menu.add_command(label="Exit", command=cb("on_closing"))

    # Top-level Settings menu with Measuring Parameter
    settings_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Measuring Parameter", command=cb("open_parameter"))

    # Make 'Measure' a top-level menu command (start directly from main Measure)
    menu_bar.add_command(label="Measure", command=cb("open_measure"))

    # 'Parameter' moved into Settings submenu

    tools_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(label="DAC/ADC", command=cb("open_adjust"))
    tools_menu.add_command(label="Sinus", command=cb("open_sinus"))
    tools_menu.add_command(label="Tunnel", command=cb("open_tunnel"))
    tools_menu.add_separator()

    tools_menu.add_command(
        label="Tunnel Simulation", command=cb("open_tunnel_simulate")
    )
    tools_menu.add_command(
        label="Measure Simulation", command=cb("open_measure_simulate")
    )

    tools_menu.add_command(label="Info Simulation", command=cb("show_simulation_info"))

    return menu_bar
