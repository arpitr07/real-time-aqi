# real-time-aqi
[Real-time AQI Data](https://dash-aqi.herokuapp.com/)

### What is it really about?

Put simply, it's a data visualization project. Having said that, data visualization requires 'data' and for any data to make sense, it has to be cleaned and processed in a way that makes the final 'visual' easy to understand and take away insights from.

For this project, the emphasis is on providing air quality indices(AQI) for locations worldwide. The project takes a path that's roughly outlined below. Needless to say, the path is nowhere close to a highway. It had it's own share of twists and turns and many of the decisions/stages had to be revisited multiple times before getting the application to it's current form. Again, this isn't the best version yet. You'll see more features being added to this application soon. I guess, I have enough to share at this stage. So here we go!

### Approach

#### Set the purpose
Get an overview of AQI levels across locations for a given country. More specifically, we are concerned about the Instant-AQI (latest available). More on this [here](https://aqicn.org/faq/2015-03-15/air-quality-nowcast-a-beginners-guide/).
#### Visualization format
Given that we are going to be looking at multiple locations within a country (spatial data), it's imperative that we go ahead with a 'Map'.
#### Data Source
At this point, we need a data source that can provide us the latest available data on AQI. There'are multiple APIs available to do just that. Hence, it is always a good idea to look at all the possible data sources and then, select one that meets our purpose.
Here are some of the many options I considered:
1. [OpenAQ API](https://docs.openaq.org)
2. [AirVisual API](https://www.airvisual.com/air-pollution-data-api)
3. [WAQI API](https://aqicn.org/json-api/doc/)

While OpenAQ has a great API that provides data at a granular level (includes concentration values for various pollutants like PM2.5, PM10, SO2, NO2, O3 and others), it is difficult to convert these concentrations into AQI values. 
Again, the conversion is really straight-forward. How? get your answers [here](https://forum.airnowtech.org/t/the-aqi-equation/169).
The challenge is that not all countries adhere to the exact same formula or concentration break-points. And they have valid [reasons](https://aqicn.org/faq/2015-03-15/air-quality-nowcast-a-beginners-guide/) for that. There are other challenges, which I discuss in this notebook.

With AirVisual API, while it's easy to get your hands on AQI levels for individual locations or AQI monitoring stations, getting data for an entire country (or for all countries) at once is not possible (at least not with their basic account). 

For reasons discussed above, I selected the WAQI API as our data-source given that the capabilities of this API meet our purpose.
#### Visualization Library
While there're many options available, I decided to go with [Folium](https://python-visualization.github.io/folium/). The library is highly intuitive to use, and it offers a high degree of interactivity.
I could also try using [Mapbox](https://plot.ly/python/scattermapbox/).

Let's take a short breathe at this point and see where we stand.

*We have a data-source that serves our purpose of having AQI levels of multiple locations across a country available with a single API call. We have an open-source data visualization library that can help us plot the spatial data (data with latitude, longitude, location) on a map, while having a high degree of interactivity at our disposal.*

At this point, we need an interface that allows a user to select the country of choice. Plus, while the visualization we get is itself interactive, we'll have to make sure, we have some means of auto-updating the map (and the underlying data) at certain specific interval (say, 1 hour).
#### A framework for building web application
As someone new to web development, I was looking for an intuitive option. That's when I found [Dash](https://dash.plot.ly). It uses Flask in the background and has enough features to meet our requirements.
#### Deploying the web application
Dash has it's own [documentation](https://dash.plot.ly/deployment) and lists various paths one could take to deploy the app.
I decide to go with [Heroku](https://www.heroku.com/) (again, I found it intuitive and easier). Other options are listed in the above documentation.

We've got the basic building blocks sorted. At least for now!
We'll take deeper dives and discuss more about each of these blocks.

To start with, let's get an insight into the kind of data we receive from the API. This notebook discusses various aspects of the data itself and how we could use it for our larger purpose.

Our next step would be to understand how folium works. Consider going through the official documentation if you're new to this library.
Otherwise, have a look at this notebook.

Now, it all comes down to Dash and how, I uses various dash componnents to put together a web application. In my opinion, it's best ot go through the example in Dash official documentation and learn the basics of the dash-components and associated callbacks.

We also make use of [dash-daq components](https://dash.plot.ly/dash-daq) to add elements like LEDDisplay for time, etc.

We'll see how to upload the project to GitHub and then use Heroku to deploy the code hosted on GitHub. I'll try to post 2 separate articles and link them here to show exactly hoe to accomplish these tasks.

Cheers!
