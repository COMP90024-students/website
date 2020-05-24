from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go
import re

def plotly_bargraph(text):
    """A wonderful function that returns figure data for three equally
    wonderful plots: wordcloud, frequency histogram and treemap"""

    # if len(text) < 1:
    #     return {}

    # topic_words = ('corona','coronavirus','covid','covid-19','covid19','viru')
    # pattern = r'|'.join(topic_words)
    # text = [re.sub(pattern,'',i) for i in text]
    # # join all documents in corpus
    # text = " ".join(text)

    word_cloud = WordCloud(stopwords=set(STOPWORDS), max_words=50,
     max_font_size=90, collocations=False)
    word_cloud.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # # get the positions
    # x_arr = []
    # y_arr = []
    # for i in position_list:
    #     x_arr.append(i[0])
    #     y_arr.append(i[1])

    # # get the relative occurence frequencies
    # new_freq_list = []
    # for i in freq_list:
    #     new_freq_list.append(i * 70)

    # trace = go.Scatter(
    #     x=x_arr,
    #     y=y_arr,
    #     textfont=dict(size=new_freq_list, color=color_list),
    #     hoverinfo="text",
    #     textposition="top center",
    #     hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
    #     mode="text",
    #     text=word_list,
    #     )

    # layout = go.Layout(
    #     {
    #         "xaxis": {
    #             "showgrid": False,
    #             "showticklabels": False,
    #             "zeroline": False,
    #             "automargin": True,
    #             "range": [-100, 250],
    #         },
    #         "yaxis": {
    #             "showgrid": False,
    #             "showticklabels": False,
    #             "zeroline": False,
    #             "automargin": True,
    #             "range": [-100, 450],
    #         },
    #         "margin": dict(t=20, b=20, l=0, r=10, pad=0),
    #         "hovermode": "closest",
    #         "plot_bgcolor": "#F6F6F4",
    #         "paper_bgcolor": "#F6F6F4",
    #     }
    # )

    # wordcloud_figure_data = {"data": [trace], "layout": layout}
    
    word_list_top = word_list[:15]
    word_list_top.reverse()
    freq_list_top = freq_list[:15]
    freq_list_top.reverse()

    frequency_figure_data = {
        "data": [
            {
                "y": word_list_top,
                "x": freq_list_top,
                "type": "bar",
                "name": "",
                "orientation": "h",
            }
        ],
        "layout": {
        "margin": dict(t=40, b=20, l=130, r=20, pad=4),
        "title":'Hashtag Relative Frequency',
        "plot_bgcolor": "#F6F6F4",
        "paper_bgcolor": "#F6F6F4",},
        }

    # return wordcloud_figure_data
    return frequency_figure_data