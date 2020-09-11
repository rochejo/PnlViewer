from bokeh.plotting import figure, ColumnDataSource
from bokeh.palettes import Spectral4
from bokeh.models import HoverTool, NumeralTickFormatter, DatetimeTickFormatter
from bokeh.models.annotations import Title


def pnl_plot(data):
    source = ColumnDataSource(data)

    hover = HoverTool(
        tooltips=[
            ('Date', '@Date'),
            ('Realized', '@Realized{,}'),
            ('Unrealized', '@Unrealized{,}'),
            ('Total', '@Total{,}'),
        ],
        formatters={
            'Date': 'datetime',
            'Realized': 'printf',
            'Unrealized': 'printf',
            'Total': 'printf'
        })

    title = Title(text='Historical Daily P&L', text_font_size='12pt')
    p = figure(x_axis_type='datetime', sizing_mode='scale_height', y_axis_label='P&L', tools=[hover], title=title)

    p.xaxis.formatter = DatetimeTickFormatter(days=['%d-%b-%y'], months=['%d-%b-%y'], years=['%d-%b-%y'])
    p.yaxis.formatter = NumeralTickFormatter(format=',')

    for col, color in zip(['Realized', 'Unrealized', 'Total'], Spectral4):
        p.line(x='Date', y=col, source=source, line_width=2, color=color, alpha=0.8, legend_label=col)

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p
