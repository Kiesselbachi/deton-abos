import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="deton Abos & Finanzen", layout="wide")
st.title("deton — Abo & Fixkosten-Management")

FILE = "abos_daten.csv"

# Initialisiere CSV mit erweiterten Spalten inklusive Abbuchungstag
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=[
        "Abo Name", "Rhythmus", "Fälligkeit Tag", "Kategorie", 
        "Zahlungskonto", "Betrag pro Zahlung", "Jahresbetrag"
    ])
    df.to_csv(FILE, index=False)
else:
    df = pd.read_csv(FILE)

st.subheader("Neues Abo / Fixkosten hinzufügen")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    name = st.text_input("Abo Name")
with col2:
    rhythmus = st.selectbox("Rhythmus", ["Monatlich", "Jährlich", "Alle 3 Jahre"])
    tag = st.number_input("Abbuchungstag", min_value=1, max_value=31, value=1)
with col3:
    betrag = st.number_input("Betrag in EUR", min_value=0.0, format="%.2f")
with col4:
    kategorie = st.selectbox(
        "Kategorie", 
        ["Miete", "Autoversicherung", "Lizenzen", "Website", "Software", "Sonstiges"]
    )
with col5:
    konto = st.selectbox("Zahlungskonto", ["deton Hauptkonto", "Kreditkarte", "Paypal", "DKB"])

if st.button("Abo speichern", type="primary"):
    if name:
        # Jahresbetrag berechnen
        if rhythmus == "Monatlich":
            j_betrag = betrag * 12
        elif rhythmus == "Jährlich":
            j_betrag = betrag
        else:
            j_betrag = betrag / 3

        neu = pd.DataFrame([{
            "Abo Name": name, 
            "Rhythmus": rhythmus, 
            "Fälligkeit Tag": int(tag), 
            "Kategorie": kategorie, 
            "Zahlungskonto": konto, 
            "Betrag pro Zahlung": betrag, 
            "Jahresbetrag": j_betrag
        }])
        df = pd.concat([df, neu], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success(f"'{name}' erfolgreich hinzugefügt!")
        st.rerun()
    else:
        st.warning("Bitte gib einen Namen für das Abo ein.")

st.divider()

st.subheader("Aktuelle Abo-Übersicht")
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Änderungen übernehmen & speichern"):
    edited.to_csv(FILE, index=False)
    st.success("Tabelle aktualisiert.")
    st.rerun()

st.divider()
st.subheader("Finanz-Auswertung & Cashflow")

if not edited.empty:
    # Metriken oben
    gesamt_jahr = edited["Jahresbetrag"].sum()
    monatliche_last = edited[edited["Rhythmus"] == "Monatlich"]["Betrag pro Zahlung"].sum()
    
    m1, m2 = st.columns(2)
    m1.metric("Gesamte Jahreslast aller Abos", f"{gesamt_jahr:,.2f} EUR")
    m2.metric("Laufende monatliche Fixkosten", f"{monatliche_last:,.2f} EUR")
    
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        # Balkendiagramm nach Kategorie
        cat_sum = edited.groupby("Kategorie")["Jahresbetrag"].sum().reset_index()
        fig1 = px.bar(cat_sum, x="Kategorie", y="Jahresbetrag", title="Jahreskosten nach Kategorie", color="Kategorie")
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        # Zahlungskonten Verteilung
        konto_sum = edited.groupby("Zahlungskonto")["Jahresbetrag"].sum().reset_index()
        fig2 = px.pie(konto_sum, values="Jahresbetrag", names="Zahlungskonto", title="Belastung nach Zahlungskonto", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
