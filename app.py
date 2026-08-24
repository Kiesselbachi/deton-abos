import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="deton Abos", layout="wide")
st.title("deton Finanzverwaltung")

FILE = "abos_daten.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=[
        "Abo Name", "Rhythmus", "Fälligkeit", "Kategorie", 
        "Zahlungskonto", "Betrag", "Jahresbetrag"
    ])
    df.to_csv(FILE, index=False)
else:
    df = pd.read_csv(FILE)

st.subheader("Neuen Datensatz anlegen")
col1, col2, col3, col4 = st.columns(4)

with col1:
    name = st.text_input("Name")
    konto = st.selectbox("Konto", ["deton Hauptkonto", "Kreditkarte", "Paypal"])
with col2:
    rhythmus = st.selectbox("Rhythmus", ["Monatlich", "Jährlich", "Alle 3 Jahre"])
    betrag = st.number_input("Betrag in EUR", min_value=0.0, format="%.2f")
with col3:
    fälligkeit = st.selectbox(
        "Fälligkeit Monat", 
        ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember", "Monatlich"]
    )
with col4:
    kategorie = st.selectbox(
        "Kategorie", 
        ["Miete", "Autoversicherung", "Lizenzen", "Website", "Software", "Sonstiges"]
    )

if st.button("Hinzufügen"):
    j_betrag = betrag * 12 if rhythmus == "Monatlich" else (betrag if rhythmus == "Jährlich" else betrag / 3)
    neu = pd.DataFrame([{
        "Abo Name": name, "Rhythmus": rhythmus, "Fälligkeit": fälligkeit, 
        "Kategorie": kategorie, "Zahlungskonto": konto, "Betrag": betrag, "Jahresbetrag": j_betrag
    }])
    df = pd.concat([df, neu], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.rerun()

st.subheader("Übersicht aller Daten")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Änderungen der Tabelle speichern"):
    edited.to_csv(FILE, index=False)
    st.success("Tabelle aktualisiert")
    st.rerun()

st.divider()
st.subheader("Auswertung")

if not edited.empty:
    gesamt = edited["Jahresbetrag"].sum()
    st.metric("Jahreslast Gesamt", f"{gesamt:,.2f} EUR")
    
    c1, c2 = st.columns(2)
    with c1:
        cat_sum = edited.groupby("Kategorie")["Jahresbetrag"].sum().reset_index()
        fig1 = px.bar(cat_sum, x="Kategorie", y="Jahresbetrag", title="Kosten nach Kategorie", color="Kategorie")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        monatlich = edited[edited["Rhythmus"] == "Monatlich"]["Betrag"].sum()
        st.metric("Monatliche Fixkosten", f"{monatlich:,.2f} EUR")
        
        rhythm_sum = edited.groupby("Rhythmus")["Jahresbetrag"].sum().reset_index()
        fig2 = px.pie(rhythm_sum, values="Jahresbetrag", names="Rhythmus", title="Verteilung der Zahlungsintervalle")
        st.plotly_chart(fig2, use_container_width=True)
