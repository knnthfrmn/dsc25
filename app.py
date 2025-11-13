from shiny import App, ui, render, reactive
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#i decided to write this using the original unchanged data
#as a result, the app calculates things like attendance rates,
#rather than simply just displaying them
#i've also written this in such a way that it can be used the dataset is edited
#for example: dropping a module

a_data = pd.read_csv("C:/Users/kenne/Desktop/datasci25/syenv/summative/dsc25/attendance_anonymised-1.csv")

#define ui
def make_ui(modules):
    "Return UI with populated dropdown."
    return ui.page_fluid(
        ui.h2("Module Attendance Tracker"),
        ui.input_select(
            "module_select",
            "Select Module:",
            choices=modules),
        ui.output_plot("attendance_plot"))

#server
#https://shiny.posit.co/py/api/core/reactive.value.html used
def server(input, output, session):
    #compute module list reactively, 
    #so this can be used with similarly formatted/edited data
    modules = reactive.Value(sorted(a_data["Long Description"].dropna().unique().tolist()))

    
    @output
    @render.plot
    #filtering and plotting
    def attendance_plot():
        selected_module = input.module_select()
        if not selected_module:
            return None

        #filter data to only show class
        mfilter = a_data[a_data["Long Description"] == selected_module]
        if mfilter.empty:
            return None

        class_size = len(mfilter["Person Code"].unique())
        daily_attendance = (
            mfilter.groupby("Planned Start Date")["Postive Marks"].sum().reset_index())
        daily_attendance["Rate"] = daily_attendance["Postive Marks"] / class_size
        daily_attendance["Planned Start Date"] = pd.to_datetime(daily_attendance["Planned Start Date"])
        daily_attendance = daily_attendance.sort_values("Planned Start Date")

        #plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(daily_attendance["Planned Start Date"], daily_attendance["Rate"], color="steelblue")
        ax.set_xlabel("Planned Start Date")
        ax.set_ylabel("Attendance Rate")
        ax.set_title(f"Attendance rate for {selected_module}")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        #^for more consistent intervals
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

app = App(make_ui(sorted(a_data["Long Description"].dropna().unique().tolist())), server)
#i hate shiny 