import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_discrimination (df, sensitive_attributes, class_name):

# ASSUMPTION: Each value of the attribute is discriminated
# For each value, we therefore apply the Preferential Sampling formulas to compute the discrimination 
# If discrimination > 0, the assumption holds true
# Otherwhise, it doesn't. This means the value is actually *privileged*
# A dictionary of sensitive attributes and values is created as such
#
# Please note the sum of records to add / remove for each priviliged value
# should be equal to the sum of records to add / removed for each discriminated value
#
# A rounding error is possible

    
    sensitive_dict = {}
    
    st.write("Records:", len(df))
    
    tot_disc = 0
    tot_pos = 0
    
    #df = X_proba
    
    for attr in sensitive_attributes:
        st.write()
        st.write("Analizing", attr, "...")
        sensitive_dict[attr] = {}
        sensitive_dict[attr]['D'] = {}
        sensitive_dict[attr]['P'] = {}
        sensitive_dict[attr]['D']['values_list'] = []
        sensitive_dict[attr]['P']['values_list'] = []
        values = df[attr].unique()
        disc_vals = []
        priv_vals = []
        disc_perc = []
        priv_perc = []
        for val in values:
            PP = df[(df[attr] != val) & (df[class_name] == 1)].values.tolist()
            PN = df[(df[attr] != val) & (df[class_name] == 0)].values.tolist()
            DP = df[(df[attr] == val) & (df[class_name] == 1)].values.tolist()
            DN = df[(df[attr] == val) & (df[class_name] == 0)].values.tolist()

            disc = len(DN) + len(DP)
            priv = len(PN) + len(PP)
            pos = len(PP) + len(DP)
            neg = len(PN) + len(DN)
            
            DP_exp = round(disc * pos / len(df))
            PP_exp = round(priv * pos / len(df))
            DN_exp = round(disc * neg / len(df))
            PN_exp = round(priv * neg / len(df))
            
            discrimination = len(PP) / (len(PP) + len(PN)) - len(DP) / (len(DP) + len(DN))
       
            if discrimination >= 0:
                status = 'D'
                sensitive_dict[attr][status][val] = {}
                print("")
                print(val, "is discriminated")
                print("Local disc:", discrimination)
                
                sensitive_dict[attr][status][val]['P'] = DP
                sensitive_dict[attr][status][val]['P_exp'] = DP_exp
                sensitive_dict[attr][status][val]['P_curr'] = len(DP)
                
                #for i in range(len(sensitive_dict[attr][status][val]['P'])):
                   # del sensitive_dict[attr][status][val]['P'][i][-1]
                                
                sensitive_dict[attr][status][val]['N'] = DN[0]
                sensitive_dict[attr][status][val]['N_exp'] = DN_exp
                sensitive_dict[attr][status][val]['N_curr'] = len(DN)
                sensitive_dict[attr][status][val]['GD'] = 100 * (abs(len(DP)-DP_exp) + abs(len(DN)-DN_exp)) / len(df)

                #for i in range(len(sensitive_dict[attr][status][val]['N'])):
                    #del sensitive_dict[attr][status][val]['N'][i][-1]
                    
                print("Global disc:", sensitive_dict[attr][status][val]['GD'])

                print("- DP:", len(sensitive_dict[attr][status][val]['P']), '· Expected:', DP_exp, 
                      '· To be added:', abs(len(DP) - DP_exp))
                print("- DN:", len(sensitive_dict[attr][status][val]['N']), '· Expected:', DN_exp, 
                      '· To be removed:', abs(len(DN) - DN_exp))
                
                tot_disc = tot_disc + abs(len(DP) - DP_exp)
                                
                disc_vals.append(val)
                disc_perc.append(round(sensitive_dict[attr][status][val]['GD'], 2))
                

            else:
                status = 'P'
                sensitive_dict[attr][status][val] = {}
                print("")
                print(val, "is privileged")
                print("Local disc:", discrimination)                
                
                sensitive_dict[attr][status][val]['P'] = DP
                sensitive_dict[attr][status][val]['P_exp'] = DP_exp
                sensitive_dict[attr][status][val]['P_curr'] = 0

                #for i in range(len(sensitive_dict[attr][status][val]['P'])):
                    #del sensitive_dict[attr][status][val]['P'][i][-1]
                    
                sensitive_dict[attr][status][val]['N'] = DN
                sensitive_dict[attr][status][val]['N_exp'] = DN_exp
                sensitive_dict[attr][status][val]['N_curr'] = 0
                sensitive_dict[attr][status][val]['GD'] = 100 * (abs(len(DP)-DP_exp) + abs(len(DN)-DN_exp)) / len(df)


                #for i in range(len(sensitive_dict[attr][status][val]['N'])):
                    #del sensitive_dict[attr][status][val]['N'][i][-1]
                    
                print("Global disc:", sensitive_dict[attr][status][val]['GD'])
                
                print("- PP:", len(sensitive_dict[attr][status][val]['P']), '· Expected:', DP_exp, 
                      '· To be removed:', abs(len(DP) - DP_exp))
                print("- PN:", len(sensitive_dict[attr][status][val]['N']), '· Expected:', DN_exp, 
                      '· To be added:', abs(len(DN) - DN_exp))
                
                tot_pos = tot_pos + abs(len(DP) - DP_exp)
                
                priv_vals.append(val)
                priv_perc.append(round(sensitive_dict[attr][status][val]['GD'], 2))
            
            sensitive_dict[attr][status]['values_list'].append(val)
            
        
        attribute_disc = sum(priv_perc)
        print("")       
        st.write("Global discrimination for", attr, attribute_disc)
        
        labels = ['Unbiased', 'Biased']
        sizes = [100 - round(attribute_disc, 2), round(attribute_disc, 2)]

        # Create pie chart
        fig, ax = plt.subplots()
        ax.pie(sizes, startangle=90, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title("Global Discrimination for " + str(attribute))

        # Display pie chart using Streamlit
        st.pyplot(fig)
        

        
        for vals, percs, stat in zip((priv_vals, disc_vals), (priv_perc, disc_perc), 
                                    ('privileged', 'discriminated')):
            
            labels = ['Unbiased, ' + str(100 - sum(percs)) + "%"]
            sizes = [100 - sum(percs)]

            for val, perc in zip(vals, percs):
                labels.append(val + ", " + str(perc) + "%")
                sizes.append(perc)

            # Create pie chart
            fig, ax = plt.subplots()
            patches, texts = ax.pie(sizes, startangle=90)
            plt.legend(patches, labels, loc="lower right")
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.tight_layout()
            plt.title(attr + " " + stat + " " + "values")

            # Display pie chart using Streamlit
            st.pyplot(fig)
                                   
    return sensitive_dict            


st.set_page_config(page_title="FairCheck")
st.title("FairCheck")

st.sidebar.subheader("Dataset")
uploaded_file = st.sidebar.file_uploader("Upload a dataset", type="csv")

cols = []



if uploaded_file:

    df = pd.read_csv(uploaded_file)

    cols = list(df.columns)

    SA = st.selectbox("Select a sensitive attribute...", cols, key=1)
    class_name = st.selectbox("Select the class...", cols, key=2)

    if SA and class_name:
        analyze_button = st.button("Analyze!")
        if analyze_button:
            get_discrimination(df, [SA], class_name)


        


st.sidebar.info("\nMade by Federico Mazzoni")


      


