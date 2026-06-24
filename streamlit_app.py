# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests 

# Create session
session = Session.builder.configs(st.secrets["snowflake"]).create()


# Sidebar
page = st.sidebar.selectbox(
    "Choose a page",
    ["Customise Your Smoothie", "Pending Smoothie Orders"]
)


# Set up sidebar navigation
#page = st.sidebar.selectbox("Navigate", ["Order Smoothie", "Pending Smoothie Orders"])

if page == "Pending Smoothie Orders":
    st.title(f":cup_with_straw: Pending Smoothie Orders ")
    st.write("Orders that need to be filled.")
    
    session = get_active_session()
    my_dataframe = session.table("smoothies.public.orders").select(col('INGREDIENTS'), col('NAME_ON_ORDER'), col('ORDER_FILLED'))
    
    st.dataframe(data=my_dataframe, use_container_width=True)


    df = session.table("smoothies.public.orders").select(
        col('INGREDIENTS'),
        col('NAME_ON_ORDER'),
        col('ORDER_FILLED')
    )

    st.dataframe(df.to_pandas(), use_container_width=True)

else:
    st.title(f":cup_with_straw: Customise Your Smoothie:cup_with_straw:")
    st.write(
      """Choose the fruits you want in your Smoothie!
      """
    )

    name_on_order = st.text_input('Name on Smoothie:')
    st.write('The name on your Smoothie will be: ', name_on_order)

#    cnx = st.connection("snowflake")
#    session = cnx_session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:'
        , my_dataframe
        , max_selections=5
        )

    if ingredients_list:
        ingredients_string = ''

        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
            st.subheader(fruit_chosen + ' Nutrion Information')

            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)  
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

        my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order) values ('""" + ingredients_string + """', '""" + name_on_order + """') """

        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered ' + name_on_order + '!', icon="✅")
 
