import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="deton Abos & Finanzen", layout="wide")
st.title("deton — Abo & Fixkosten-Management")

FILE = "abos_daten.csv"

monate_de = ["Januar","Februar","März","April","Mai","Juni","Juli",
             "August","September","Oktober","November","Dezember"]

# Initialisiere CSV mit erweiterten Spalten
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=[
        "Abo Name", "Rhythmus", "Fälligkeit Tag", "Abrechnungsmonat",
        "Letzte Abrechnung Jahr", "Kategorie", "Zahlungskonto",
        "Betrag pro Zahlung", "Jahresbetrag"
    ])
    df.to_csv(FILE, index=False)
else:
    df = pd.read_csv(FILE)
    for col in ["Abrechnungsmonat", "Letzte Abrechnung Jahr"]:
        if col not in df.columns:
            df[col] = ""

st.subheader("Neues Abo / Fixkosten hinzufügen")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    name = st.text_input("Abo Name")
with col2:
    rhythmus = st.selectbox("Rhythmus", ["Monatlich", "Jährlich", "Alle 3 Jahre"])
with col3:
    betrag = st.number_input("Betrag in EUR", min_value=0.0, format="%.2f")
with col4:
    kategorie = st.selectbox(
        "Kategorie", 
        ["Miete", "Autoversicherung", "Lizenzen", "Website", "Software", "Sonstiges"]
    )
with col5:
    konto = st.selectbox("Zahlungskonto", ["deton Hauptkonto", "Kreditkarte", "Paypal", "DKB"])

# Zeitliche Angaben, abhängig vom Rhythmus
monat = None
letzte_jahr = None

if rhythmus == "Monatlich":
    dcol1, = st.columns(1)
    with dcol1:
        tag = st.number_input("Abbuchungstag", min_value=1, max_value=31, value=1)

elif rhythmus == "Jährlich":
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        tag = st.number_input("Abbuchungstag", min_value=1, max_value=31, value=1)
    with dcol2:
        monat_name = st.selectbox("Abrechnungsmonat", monate_de)
        monat = monate_de.index(monat_name) + 1

else:  # Alle 3 Jahre
    dcol1, dcol2, dcol3 = st.columns(3)
    with dcol1:
        tag = st.number_input("Abbuchungstag", min_value=1, max_value=31, value=1)
    with dcol2:
        monat_name = st.selectbox("Abrechnungsmonat", monate_de)
        monat = monate_de.index(monat_name) + 1
    with dcol3:
        letzte_jahr = st.number_input("Letzte Abrechnung (Jahr)", min_value=2000, max_value=2100, value=pd.Timestamp.now().year)

if st.button("Abo speichern", type="primary"):
    if name:
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
            "Abrechnungsmonat": monat if monat else "",
            "Letzte Abrechnung Jahr": int(letzte_jahr) if letzte_jahr else "",
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
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="abo_table")
col_s1, col_s2 = st.columns([1, 4])
with col_s1:
    if st.button("Speichern / Löschen anwenden", type="primary"):
        edited.to_csv(FILE, index=False)
        st.success("Änderungen erfolgreich gespeichert!")
        st.rerun()
st.divider()

st.subheader("Finanz-Auswertung & Cashflow")
if not edited.empty:
    gesamt_jahr = edited["Jahresbetrag"].sum()
    monatliche_last = edited[edited["Rhythmus"] == "Monatlich"]["Betrag pro Zahlung"].sum()
    
    m1, m2 = st.columns(2)
    m1.metric("Gesamte Jahreslast aller Abos", f"{gesamt_jahr:,.2f} EUR")
    m2.metric("Laufende monatliche Fixkosten", f"{monatliche_last:,.2f} EUR")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        cat_sum = edited.groupby("Kategorie")["Jahresbetrag"].sum().reset_index()
        fig1 = px.bar(cat_sum, x="Kategorie", y="Jahresbetrag", title="Jahreskosten nach Kategorie", color="Kategorie")
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        konto_sum = edited.groupby("Zahlungskonto")["Jahresbetrag"].sum().reset_index()
        fig2 = px.pie(konto_sum, values="Jahresbetrag", names="Zahlungskonto", title="Belastung nach Zahlungskonto", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Monatlicher Cashflow (Kalenderjahr)")

if not edited.empty:
    jahr_auswahl = st.selectbox(
        "Jahr für die Kalenderansicht",
        options=list(range(pd.Timestamp.now().year, pd.Timestamp.now().year + 4))
    )

    monatslast = {m: 0.0 for m in range(1, 13)}

    for _, row in edited.iterrows():
        rhythmus_r = row["Rhythmus"]
        betrag_r = row["Betrag pro Zahlung"]

        if rhythmus_r == "Monatlich":
            for m in range(1, 13):
                monatslast[m] += betrag_r

        elif rhythmus_r == "Jährlich":
            monat_r = row.get("Abrechnungsmonat")
            if pd.notna(monat_r) and monat_r != "":
                monatslast[int(monat_r)] += betrag_r

        elif rhythmus_r == "Alle 3 Jahre":
            monat_r = row.get("Abrechnungsmonat")
            letzte_jahr_r = row.get("Letzte Abrechnung Jahr")
            if pd.notna(monat_r) and monat_r != "" and pd.notna(letzte_jahr_r) and letzte_jahr_r != "":
                diff = jahr_auswahl - int(letzte_jahr_r)
                if diff >= 0 and diff % 3 == 0:
                    monatslast[int(monat_r)] += betrag_r

    cashflow_df = pd.DataFrame({
        "Monat": monate_de,
        "Belastung": [monatslast[m] for m in range(1, 13)]
    })

    fig3 = px.bar(
        cashflow_df, x="Monat", y="Belastung",
        title=f"Finanzielle Belastung pro Monat ({jahr_auswahl})",
        text_auto=".2s"
    )
    st.plotly_chart(fig3, use_container_width=True)
