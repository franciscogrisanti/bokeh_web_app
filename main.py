import pandas as pd
import numpy as np
from os.path import dirname, join
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource,Panel,HoverTool, CustomJS, Select
from bokeh.models.widgets import Dropdown, CheckboxGroup,Slider,RangeSlider,Tabs, TableColumn, DataTable, Button
from bokeh.layouts import row, WidgetBox
from bokeh.palettes import Category20_16
from bokeh.io import curdoc,show
from bokeh.themes import Theme

import yaml

population = pd.read_csv(join(dirname(__file__),'data','spirometry_anthropometric_clean.csv'))
theme = Theme(join(dirname(__file__),"theme.yaml"))

# Make plot with histogram and return tab


def histogram_tab(population):
    #initial parameters
    # Function to make a dataset for histogram based on a list of carriers
    # a minimum delay, maximum delay, and histogram bin widt
    
    def make_dataset(gender_list=list(["Male","Female"]),
                    age_start=2,
                    age_end=26,
                    weight_start=10,
                    weight_end=218,
                    height_start=80,
                    height_end=200,
                    bmi_start=11.2,
                    bmi_end=67.3,
                    bin_width = 25
                    ):
        
        hist_population = pd.DataFrame(columns=['proportion', 'left', 'right', 
                                        'f_proportion', 'f_interval','gender','color'])	  
        
                
        for i, gender_name in enumerate(gender_list):
            if gender_name == 'All':
                subset = population
            else:
                subset = population[population['GENDER2'] == gender_name]	
            subset = subset[(subset.AGE > age_start) 
                                & (subset.AGE < age_end)
                                & (subset.WEIGHT > weight_start)
                                & (subset.WEIGHT < weight_end)
                                & (subset.HEIGHT > height_start)
                                & (subset.HEIGHT < height_end)
                                & (subset.BMI > bmi_start)
                                    & (subset.BMI < bmi_end)
                            ]
                            

            arr_hist, edges = np.histogram(subset['FVC_MAX'], bins = np.arange(np.min(subset['FVC_MAX']), np.max(subset['FVC_MAX']) + bin_width, bin_width))
            # Divide the counts by the total to get a proportion
            arr_df = pd.DataFrame({'proportion': arr_hist , 'left': edges[:-1], 'right': edges[1:] })
            
            
            # Format the proportion 
            arr_df['f_proportion'] = ['%0.5f' % proportion for proportion in arr_df['proportion']]
            
            # Format the interval
            arr_df['f_interval'] = ['%d to %d ml' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]
                
            #assign the carrier for labels
            arr_df['gender'] = gender_name
            #color each carrier differently
            arr_df['color'] = Category20_16[i]
            # Add to the overall dataframe
            hist_population = hist_population.append(arr_df)
        # Overall dataframe
        hist_population = hist_population.sort_values(['gender', 'left'])
        
        #Add to the overall dataframe
        return ColumnDataSource(hist_population)   
        
    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'
        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'
        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'
        return p
    
    def make_plot(src):
        # Blank plot with correct labels
        p = figure(plot_width = 700, plot_height = 700, 
                title = 'Force Vital Capacity',
                x_axis_label = 'FVC (ml)', y_axis_label = 'Count',background_fill_color="#2E3332")
        # Quad glyphs to create a histogram
        p.quad(source = src, bottom = 0, top = 'proportion', left = 'left', right='right',
            color = 'color', fill_alpha = 0.7,hover_fill_color = 'color', legend = 'gender', 
            hover_fill_alpha = 1.0, line_color = 'black') 
        #pdf line
        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Gender', '@gender'), 
                                        ('ml', '@f_interval'),
                                        ('Proportion', '@f_proportion')],
                            mode='vline')
        p.add_tools(hover)
        
        p = style(p)
        return p
    
    def update(attr,old,new):
        genders_to_plot = [select_gender.labels[i] for i in select_gender.active]
        
        new_src = make_dataset(genders_to_plot, 
                    age_start = age_select.value[0],
                    age_end = age_select.value[1],
                    weight_start = weight_select.value[0],
                    weight_end = weight_select.value[1],
                    height_start = height_select.value[0],
                    height_end = height_select.value[1],
                    bmi_start = bmi_select.value[0],
                    bmi_end = bmi_select.value[1],
                    bin_width = binwidth_select.value)
        
        src.data.update(new_src.data)
            
    available_gender = list(['Male','Female','All'])
    available_gender.sort()
    gender_colors = Category20_16
    gender_colors.sort()

    select_gender = CheckboxGroup(labels=list(['Male','Female','All']),active = [0,1,2])
    
    select_gender.on_change('active', update)
    
    #binwidth select
    binwidth_select = Slider(start=1,end=600,step = 1,value=60,title='Bin Width')
    binwidth_select.on_change('value', update)	
    #age range select
    age_select = RangeSlider(start=1,end=25,value=(1, 28),step=1,title='Range of Age')
    age_select.on_change('value', update)
    #weight range
    weight_select =RangeSlider(start=10,end=200,value=(10, 200),step=1,title='Range of Weight')
    weight_select.on_change('value', update)
    #height range select
    height_select = RangeSlider(start=80,end=200,value=(80, 200),step=1,title='Range of Height')
    height_select.on_change('value', update)
    #BMI range select
    bmi_select = RangeSlider(start= 10,end=60,value=(10, 60),step=0.5,title='Range of Body Mass Index')
    bmi_select.on_change('value', update)
        
    # Initial carriers and data source
    initial_gender = [select_gender.labels[i] for i in select_gender.active]		
    
    src = make_dataset(initial_gender, 
                        age_start = age_select.value[0],
                        age_end = age_select.value[1],
                        weight_start = weight_select.value[0],
                        weight_end = weight_select.value[1],
                        height_start = height_select.value[0],
                        height_end = height_select.value[1],
                        bmi_start = bmi_select.value[0],
                        bmi_end = bmi_select.value[1],
                        bin_width = binwidth_select.value)
                            

    p = make_plot(src)
    
    # Put controls in a single element
    controls = WidgetBox(select_gender,binwidth_select, age_select, weight_select, bmi_select, height_select)
    # Create a row layout
    layout = row(controls, p)
    # Make a tab with the layout 
    tab = Panel(child=layout, title = 'Histogram')
    
    return tab

#########################################################################################################################################
##################################                        SCATTER TAB                  ##################################################
#########################################################################################################################################

def scatter_tab(population): 
    def make_dataset(gender_list=list(['Male']),
                    age_start=2,
                    age_end=26,
                    weight_start=10,
                    weight_end=218,
                    height_start=80,
                    height_end=200,
                    bmi_start=11.2,
                    bmi_end=67.3,
                    bin_width = 25,
                    x_axis ='SESSION_IQR',
                    y_axis ='SESSION_STD'
                    ):
        gender_list = sorted(gender_list)                    
        plot_population = pd.DataFrame(columns=[x_axis , y_axis ,'gender','color'])
        if len(gender_list) == 0:
            plot_population = pd.DataFrame(columns=[x_axis , y_axis ,'gender','color'])
        else:
            for i, gender_name in enumerate(gender_list):
                if gender_name == 'All':
                    subset = population
                else:
                    subset = population[population['GENDER2'] == gender_name]	
                    subset = subset[(subset.AGE > age_start) 
                                    & (subset.AGE < age_end)
                                    & (subset.WEIGHT > weight_start)
                                    & (subset.WEIGHT < weight_end)
                                    & (subset.HEIGHT > height_start)
                                    & (subset.HEIGHT < height_end)
                                    & (subset.BMI > bmi_start)
                                        & (subset.BMI < bmi_end)
                                ]
                    
                
                arr_df = pd.DataFrame({'SEQN': subset['SEQN'], x_axis : subset[x_axis] , y_axis : subset[y_axis] })   
                arr_df['gender'] = gender_name
                arr_df['color'] = Category20_16[i]
                arr_df = arr_df[['SEQN',x_axis,y_axis,'gender','color']]
                
                if gender_name == "Male":
                    arr_df1 = arr_df
                elif gender_name == "Female":
                    arr_df2 = arr_df
                else:
                    arr_df3 = arr_df
                    
        if len(gender_list) == 1:
            plot_population = arr_df
            plot_population = plot_population.sort_values(['gender','SEQN'])
            plot_population = plot_population[['SEQN',x_axis,y_axis,'gender','color']]
            plot_population = plot_population.reset_index(drop=True)
        elif len(gender_list) == 2:
            if gender_list[0] == "Female":
                plot_population = arr_df1.append(arr_df2, ignore_index=True)
                plot_population = plot_population.sort_values(['gender','SEQN'])
                plot_population = plot_population.reset_index(drop=True)
            elif gender_list[1] == "Female":
                plot_population = arr_df3.append(arr_df2, ignore_index=True)
                plot_population = plot_population.sort_values(['gender','SEQN'])
                plot_population = plot_population.reset_index(drop=True)
            else:
                plot_population = arr_df1.append(arr_df3, ignore_index=True)
                plot_population = plot_population.sort_values(['gender','SEQN'])
                plot_population = plot_population.reset_index(drop=True)
        elif len(gender_list) == 3:
            plot_population = arr_df1.append(arr_df2, ignore_index=True)
            plot_population = plot_population.append(arr_df3, ignore_index=True)
            plot_population = plot_population.sort_values(['gender','SEQN'])
            plot_population = plot_population.reset_index(drop=True)
                
        
        return ColumnDataSource(plot_population)   
    
    
    def make_plot(src):
        p=figure()
        menu = [('Raw Curve Sequence Number','RAW_CURVE',), 
                ('Force Vital Capacity (ml)','FVC_MAX'), 
                ('Force Vital Capacity (ml) at 1sec','FEV1'), 
                ('Force Vital Capacity (ml) at 3sec','FEV3'), 
                ('Force Vital Capacity (ml) at 6sec','FEV6'),
                ('Peak expiratory flow (ml)','PEAK_EXPIRATORY'), 
                ('Max-Mid expiratory flow (ml)','MAX_MID_EXPIRATORY'), 
                ('Pseudo PSU','PSEUDO_PSU'), 
                ('Age (years)','AGE'), 
                ('Gender','GENDER2'),
                ('Height (cm)', 'HEIGHT'), 
                ('Weight (kg)','WEIGHT'), 
                ('Body mass index (kg/m2)','BMI'), 
                ('Session best FVC','SESSION_BEST'), 
                ('Session mean FVC','SESSION_MEAN'),
                ('Session std FVC','SESSION_STD'), 
                ('Session median FVC','SESSION_MEDIAN'), 
                ('Session iqr FVC','SESSION_IQR'), 
                ('Session minimum FVC','SESSION_MINIMUM'),
                ('Session maximum FVC','SESSION_MAXIMUM'), 
                ('Session max distance FVC','SESSION_MAX_DISTANCE'), 
                ('Session median distance FVC','SESSION_MEDIAN_DISTANCE')]
        if len(src.column_names) == 5:
            for i in range(22):
                if menu[i][1] == src.column_names[1]:
                        titulo_x = menu[i][0]
                        titulo_y = menu[i][0]
                        break
            xs=src.column_names[1]
            ys=src.column_names[1]
            gs=src.column_names[2]
            zs=src.column_names[3]
            x_title = titulo_x.title()
            y_title = titulo_y.title()
            kw = dict()
            kw['title'] = "%s vs %s" % (x_title, y_title)
            # Blank plot with correct labels
            p = figure(plot_width = 700, plot_height = 700,background_fill_color="#2E3332",**kw)
            p.xaxis.axis_label = x_title
            p.yaxis.axis_label = y_title
            # Quad glyphs to create a histogram
            p.circle(source=src,x=xs , y=ys , size=7, color=zs,legend=gs,fill_alpha = 0.7)
#        
        if len(src.column_names) == 6:
            for i in range(22):
                if menu[i][1] == src.column_names[1]:
                        titulo_x = menu[i][0]
                if menu[i][1] == src.column_names[2]:        
                        titulo_y = menu[i][0]                      
            xs=src.column_names[1]
            ys=src.column_names[2]
            gs=src.column_names[3]
            zs=src.column_names[4]
            x_title = titulo_x.title()
            y_title = titulo_y.title()
            kw = dict()
            kw['title'] = "%s vs %s" % (x_title, y_title)
            # Blank plot with correct labels
            p = figure(plot_width = 700, plot_height = 700,background_fill_color="#2E3332",**kw)
            p.xaxis.axis_label = x_title
            p.yaxis.axis_label = y_title
            # Quad glyphs to create a histogram
            p.circle(source=src,x=xs , y=ys , size=7, color=zs,legend=gs,fill_alpha = 0.7)   
        return p
    
    def update():
        genders_to_plot = [select_gender.labels[i] for i in select_gender.active]
        new_src = make_dataset(genders_to_plot, 
                    age_start = age_select.value[0],
                    age_end = age_select.value[1],
                    weight_start = weight_select.value[0],
                    weight_end = weight_select.value[1],
                    height_start = height_select.value[0],
                    height_end = height_select.value[1],
                    bmi_start = bmi_select.value[0],
                    bmi_end = bmi_select.value[1],
                    x_axis = select_x.value,
                    y_axis = select_y.value)
        
        layout.children[1] = make_plot(new_src)
    #gender selection
    available_gender = list(['Male','Female','All'])
    available_gender.sort()
    gender_colors = Category20_16
    gender_colors.sort()
    select_gender = CheckboxGroup(labels=list(['Male','Female','All']),active = [0,1,2])    
    select_gender.on_change('active', lambda attr, old, new: update())
    #age range select
    age_select = RangeSlider(start=1,end=25,value=(1, 28),step=1,title='Range of Age')
    age_select.on_change('value', lambda attr, old, new: update())
    #weight range
    weight_select =RangeSlider(start=10,end=200,value=(10, 200),step=1,title='Range of Weight')
    weight_select.on_change('value', lambda attr, old, new: update())
    #height range select
    height_select = RangeSlider(start=80,end=200,value=(80, 200),step=1,title='Range of Height')
    height_select.on_change('value', lambda attr, old, new: update())
    #BMI range select
    bmi_select = RangeSlider(start= 10,end=60,value=(10, 60),step=0.5,title='Range of Body Mass Index')
    bmi_select.on_change('value', lambda attr, old, new: update())
    
    menu = [('Raw Curve Sequence Number','RAW_CURVE',), 
            ('Force Vital Capacity (ml)','FVC_MAX'), 
            ('Force Vital Capacity (ml) at 1sec','FEV1'), 
            ('Force Vital Capacity (ml) at 3sec','FEV3'), 
            ('Force Vital Capacity (ml) at 6sec','FEV6'),
            ('Peak expiratory flow (ml)','PEAK_EXPIRATORY'), 
            ('Max-Mid expiratory flow (ml)','MAX_MID_EXPIRATORY'), 
            ('Pseudo PSU','PSEUDO_PSU'), 
            ('Age (years)','AGE'), 
            ('Gender','GENDER2'),
            ('Height (cm)', 'HEIGHT'), 
            ('Weight (kg)','WEIGHT'), 
            ('Body mass index (kg/m2)','BMI'), 
            ('Session best FVC','SESSION_BEST'), 
            ('Session mean FVC','SESSION_MEAN'),
            ('Session std FVC','SESSION_STD'), 
            ('Session median FVC','SESSION_MEDIAN'), 
            ('Session iqr FVC','SESSION_IQR'), 
            ('Session minimum FVC','SESSION_MINIMUM'),
            ('Session maximum FVC','SESSION_MAXIMUM'), 
            ('Session max distance FVC','SESSION_MAX_DISTANCE'), 
            ('Session median distance FVC','SESSION_MEDIAN_DISTANCE')]
    
    #select x axis
    select_x = Dropdown(label='X Axis', button_type="warning", value='SESSION_IQR', menu=menu)
    select_x.on_change('value', lambda attr, old, new: update())
    #select y axis
    select_y = Dropdown(label='Y Axis', button_type="warning", value='SESSION_STD', menu=menu)
    select_y.on_change('value', lambda attr, old, new: update())


    # Initial carriers and data source
    initial_gender = [select_gender.labels[i] for i in select_gender.active]		
    
    src = make_dataset(initial_gender, 
                        age_start = age_select.value[0],
                        age_end = age_select.value[1],
                        weight_start = weight_select.value[0],
                        weight_end = weight_select.value[1],
                        height_start = height_select.value[0],
                        height_end = height_select.value[1],
                        bmi_start = bmi_select.value[0],
                        bmi_end = bmi_select.value[1],
                        x_axis = select_x.value,
                        y_axis= select_y.value
                        )
#    p = make_plot(src)                       
    # Put controls in a single element
    controls = WidgetBox(select_gender, age_select, weight_select, bmi_select, height_select, select_x, select_y)
    # Create a row layout
    layout = row(controls, make_plot(src))
    # Make a tab with the layout 
    tab2 = Panel(child=layout, title = 'Scatter')
    update()
    return tab2

def table_tab(df):

    source = ColumnDataSource(data=dict())

    def update():
        current = df       
        if select_gender.value == "Male":
            current = df[(df['GENDER2'] == 'Male')]
        elif select_gender.value == "Female":
            current = df[(df['GENDER2'] == 'Female')]
        elif select_gender.value == "All":
            current = df
            
        current = current[ (current['HEIGHT'] >= height_select.value[0]) & (current['HEIGHT'] <= height_select.value[1])
                            & (current['WEIGHT'] >= weight_select.value[0]) & (current['WEIGHT'] <= weight_select.value[1])
                            & (current['AGE'] >= age_select.value[0]) & (current['AGE'] <= age_select.value[1])
                            & (current['BMI'] >= bmi_select.value[0]) & (current['BMI'] <= bmi_select.value[1])
                        ].dropna()

        source.data = {
            'SEQN'                      : current.SEQN,
            'RAW_CURVE'                 : current.RAW_CURVE,
            'FVC_MAX'                   : current.FVC_MAX,
            'FEV1'                      : current.FEV1,
            'FEV3'                      : current.FEV3,
            'FEV6'                      : current.FEV6,
            'PEAK_EXPIRATORY'           : current.PEAK_EXPIRATORY,
            'MAX_MID_EXPIRATORY'        : current.MAX_MID_EXPIRATORY,
            'PSEUDO_PSU'                : current.PSEUDO_PSU,
            'AGE'                       : current.AGE,
            'GENDER2'                   : current.GENDER2,
            'GENDER'                    : current.GENDER,
            'HEIGHT'                    : current.HEIGHT,
            'WEIGHT'                    : current.WEIGHT,
            'BMI'                       : current.BMI,
            'SESSION_BEST'              : current.SESSION_BEST,
            'SESSION_MEAN'              : current.SESSION_MEAN,
            'SESSION_STD'               : current.SESSION_STD,
            'SESSION_MEDIAN'            : current.SESSION_MEDIAN,
            'SESSION_IQR'               : current.SESSION_IQR,
            'SESSION_MINIMUM'           : current.SESSION_MINIMUM,
            'SESSION_MAXIMUM'           : current.SESSION_MAXIMUM,
            'SESSION_MAX_DISTANCE'      : current.SESSION_MAX_DISTANCE,
            'SESSION_MEDIAN_DISTANCE'   : current.SESSION_MEDIAN_DISTANCE
                    }
    
    
    menu = [("All", "All"), ("Male", "Male"), ("Female", "Female")]
    select_gender = Dropdown(label="Gender Selection", button_type="warning", menu=menu)
    select_gender.on_change('value', lambda attr, old, new: update())
    
    #height range select
    height_select = RangeSlider(title="Range of Height", start=80, end=200, value=(80, 200), step=0.5)
    height_select.on_change('value', lambda attr, old, new: update())
    #height range select
    age_select = RangeSlider(title="Range of Age", start=1, end=28, value=(1, 28), step=1)
    age_select.on_change('value', lambda attr, old, new: update())
    #weight range select
    weight_select = RangeSlider(title="Range of Weight", start=10, end=200, value=(10, 200), step=1)
    weight_select.on_change('value', lambda attr, old, new: update())
    #height range select
    bmi_select = RangeSlider(title="Range of Body Mass Index", start=10, end=60, value=(10, 60), step=0.5)
    bmi_select.on_change('value', lambda attr, old, new: update())

    button = Button(label="Download", button_type="success")
    button.callback = CustomJS(args=dict(source=source),code=open(join(dirname(__file__), "download.js")).read())

    columns = [
        TableColumn(field='SEQN', title='SEQN'),
        TableColumn(field='FVC_MAX', title='FVC (ml)'),
        TableColumn(field='AGE', title='AGE (years)'),
        TableColumn(field='GENDER2', title='GENDER'),
        TableColumn(field='HEIGHT', title='HEIGHT (cm)'),
        TableColumn(field='BMI', title='BMI'),
        TableColumn(field="SESSION_BEST", title='SESSION MAXIMUM (ml)')
                    ]
    data_table = DataTable(source=source, columns=columns, width=1000)


    # Put controls in a single element
    controls = WidgetBox(select_gender, age_select, weight_select, bmi_select, height_select,button)
    # Create a row layout
    layout = row(controls,data_table)
    # Make a tab with the layout 
    tab = Panel(child=layout, title = 'Summary Table')
    update()

    return tab

# Create each of the tabs
tab1 = histogram_tab(population)
tab2 = scatter_tab(population)
tab3 = table_tab(population)


# Put all the tabs into one application
tabs = Tabs(tabs = [tab1,tab2,tab3])

# Put the tabs in the current document for display
doc = curdoc()
doc.theme = theme
doc.add_root(tabs)
doc.title = "Web app - Grisanti"


