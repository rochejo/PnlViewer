from bokeh.plotting import curdoc, figure, ColumnDataSource
from bokeh.palettes import Spectral4
from bokeh.models import HoverTool, NumeralTickFormatter, DatetimeTickFormatter
from bokeh.models.annotations import Title


def pnl_chart(data):
    """
    Creates a chart to display P&L
    Parameters
    ----------
    data : DataFrame, with the following columns: Date, Realized, Unrealized, Total
    Returns
    -------
    Figure
    """
    source = ColumnDataSource(data.cumsum())

    title = Title(text='Historical Daily P&L', text_font_size='14pt', align = 'center')

    p = figure(x_axis_type='datetime', sizing_mode='scale_height', title=title)

    p.xaxis.formatter = DatetimeTickFormatter(days=['%d-%b-%y'], months=['%d-%b-%y'], years=['%d-%b-%y'])
    p.xaxis.major_label_text_font_size = '10pt'
    p.yaxis.formatter = NumeralTickFormatter(format=',')
    p.yaxis.major_label_text_font_size = '10pt'

    for col, color in zip(['Realized', 'Unrealized', 'Total'], Spectral4):
        p.line(x='Date', y=col, source=source, line_width=2, color=color, alpha=0.8, legend_label=col)

    hover = HoverTool(
        tooltips=[
            ('Realized', '@Realized{,}'),
            ('Unrealized', '@Unrealized{,}'),
            ('Total', '@Total{,}'),
        ],
        formatters={
            'Date': 'datetime',
            'Realized': 'printf',
            'Unrealized': 'printf',
            'Total': 'printf'
        },
        mode='vline',
        renderers=[p.renderers[-1]]
    )

    p.add_tools(hover)
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p


def view_pnl(data):
    """
    Render P&L chart
    Parameters
    ----------
    data : DataFrame, with the following columns: Date, Realized, Unrealized, Total
    """
    chart = pnl_chart(data)
    curdoc().title = 'P&L Viewer (beta)'
    curdoc().add_root(chart)