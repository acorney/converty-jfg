"""Design tokens and stylesheet."""

# Brand colours
GREEN = "#006838"
GREEN_DEEP = "#004A28"
GREEN_SECONDARY = "#009445"
GREEN_ACCENT = "#8CC63F"
TINT_FILL = "#F3F8EC"
TINT_FILL_ALT = "#EEF6E3"
TINT_BORDER = "#E2EED2"

INK_900 = "#333333"
INK_700 = "#54595F"
INK_500 = "#7F7F7F"
INK_400 = "#939598"

BORDER = "#CACBCC"
HAIRLINE = "#EFEFEF"
SURFACE = "#F7F6F3"

ERROR_TEXT = "#BC4B3C"
ERROR_BG = "#FCF4F1"
ERROR_BORDER = "#EFD8D1"

WHITE = "#FFFFFF"

APP_STYLESHEET = f"""
/* ---- Global ---- */
QWidget {{
    font-family: 'Montserrat', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {INK_900};
    background-color: {WHITE};
}}

/* ---- Main window ---- */
QMainWindow {{
    background: {WHITE};
}}

/* ---- Title bar area ---- */
#titleBar {{
    background: {WHITE};
    border-bottom: 1px solid {HAIRLINE};
}}
#titleLabel {{
    font-size: 13px;
    font-weight: 600;
    color: {INK_700};
}}
#convertyBadge {{
    font-size: 10px;
    font-weight: 700;
    color: {GREEN};
    background: {TINT_FILL};
    border: 1px solid {TINT_BORDER};
    border-radius: 4px;
    padding: 1px 5px;
    letter-spacing: 1px;
}}

/* ---- Left column ---- */
#leftPanel {{
    background: {WHITE};
    border-right: 1px solid {HAIRLINE};
    padding: 22px;
}}
#arrowHeading {{
    font-size: 17px;
    font-weight: 600;
    color: {INK_700};
}}
#arrowSubheading {{
    font-size: 13px;
    color: {INK_500};
}}

/* ---- Drop zone ---- */
#dropZone {{
    border: 2px dashed {BORDER};
    border-radius: 9px;
    background: {SURFACE};
    padding: 20px;
}}
#dropZone:hover {{
    border-color: {GREEN};
}}
#dropZoneLabel {{
    font-size: 13px;
    font-weight: 500;
    color: {INK_700};
}}
#dropZoneSubLabel {{
    font-size: 12px;
    color: {INK_500};
}}

/* ---- Buttons ---- */
QPushButton {{
    font-size: 14px;
    font-weight: 600;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}}
#btnPrimary {{
    background: {GREEN};
    color: {WHITE};
}}
#btnPrimary:hover {{
    background: {GREEN_DEEP};
}}
#btnPrimary:disabled {{
    background: #D6D9D7;
    color: {INK_400};
}}
#btnOutline {{
    background: transparent;
    color: {GREEN};
    border: 1.5px solid {GREEN};
}}
#btnOutline:hover {{
    background: {TINT_FILL};
}}
#btnCancel {{
    background: transparent;
    color: {INK_700};
    border: 1.5px solid {BORDER};
}}
#btnCancel:hover {{
    background: {SURFACE};
}}

/* ---- Format toggle ---- */
#formatToggle {{
    background: {SURFACE};
    border: 1.5px solid {BORDER};
    border-radius: 6px;
    padding: 2px;
}}
#fmtBtn {{
    background: transparent;
    color: {INK_500};
    border: none;
    border-radius: 5px;
    font-size: 13px;
    font-weight: 600;
    padding: 5px 18px;
}}
#fmtBtnActive {{
    background: {GREEN};
    color: {WHITE};
    border: none;
    border-radius: 5px;
    font-size: 13px;
    font-weight: 600;
    padding: 5px 18px;
}}

/* ---- Save-to row ---- */
#saveToLabel {{
    font-size: 12px;
    color: {INK_500};
}}
#saveToPath {{
    font-size: 12px;
    color: {INK_700};
    font-weight: 500;
}}
#btnChange {{
    font-size: 12px;
    color: {GREEN};
    background: transparent;
    border: none;
    padding: 0;
    font-weight: 600;
}}
#btnChange:hover {{
    text-decoration: underline;
}}

/* ---- Progress card ---- */
#progressCard {{
    background: {TINT_FILL};
    border: 1px solid {TINT_BORDER};
    border-radius: 9px;
    padding: 14px;
}}
#progressLabel {{
    font-size: 11px;
    font-weight: 700;
    color: {INK_500};
    letter-spacing: 1px;
    text-transform: uppercase;
}}
#progressPercent {{
    font-size: 22px;
    font-weight: 700;
    color: {GREEN};
}}
#progressNow {{
    font-size: 12px;
    color: {INK_500};
}}
QProgressBar {{
    border: none;
    border-radius: 3px;
    background: {TINT_BORDER};
    height: 7px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {GREEN};
    border-radius: 3px;
}}

/* ---- Error card ---- */
#errorCard {{
    background: {ERROR_BG};
    border: 1px solid {ERROR_BORDER};
    border-radius: 9px;
    padding: 14px;
}}
#errorCardText {{
    font-size: 12px;
    color: {ERROR_TEXT};
}}

/* ---- Done card ---- */
#doneCard {{
    background: {TINT_FILL};
    border: 1px solid {TINT_BORDER};
    border-radius: 9px;
    padding: 14px;
}}
#doneCardText {{
    font-size: 12px;
    color: {INK_700};
}}

/* ---- Right panel ---- */
#rightPanel {{
    background: {WHITE};
}}
#queueHeader {{
    font-size: 11px;
    font-weight: 700;
    color: {INK_500};
    letter-spacing: 1px;
}}
#queueCount {{
    font-size: 11px;
    color: {INK_400};
}}

/* ---- Queue scroll area ---- */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    width: 6px;
    background: {SURFACE};
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}

/* ---- File row ---- */
#fileRow {{
    border-bottom: 1px solid {HAIRLINE};
    padding: 10px 16px;
    background: {WHITE};
}}
#fileRowProcessing {{
    border-bottom: 1px solid {HAIRLINE};
    padding: 10px 16px;
    background: #FCFDFA;
}}
#fileRowError {{
    border-bottom: 1px solid {HAIRLINE};
    padding: 10px 16px;
    background: {ERROR_BG};
}}
#fileName {{
    font-size: 13px;
    font-weight: 500;
    color: {INK_700};
}}
#fileMeta {{
    font-size: 12px;
    color: {INK_400};
}}
#fileErrorMsg {{
    font-size: 12px;
    color: {ERROR_TEXT};
}}

/* ---- Status pills ---- */
#pillPending {{
    background: {SURFACE};
    color: {INK_500};
    border-radius: 999px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}}
#pillProcessing {{
    background: {TINT_FILL};
    color: {GREEN};
    border-radius: 999px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}}
#pillDone {{
    background: {TINT_FILL_ALT};
    color: {GREEN_SECONDARY};
    border-radius: 999px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}}
#pillError {{
    background: {ERROR_BG};
    color: {ERROR_TEXT};
    border-radius: 999px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}}

/* ---- Run log ---- */
#logPanel {{
    border-top: 1px solid {HAIRLINE};
    background: {WHITE};
    padding: 10px 16px;
}}
#logHeader {{
    font-size: 11px;
    font-weight: 700;
    color: {INK_500};
    letter-spacing: 1px;
}}
#logArea {{
    font-family: 'Cascadia Mono', 'Consolas', monospace;
    font-size: 11px;
    color: {INK_500};
    background: transparent;
    border: none;
}}
#logLineSuccess {{
    color: {GREEN_SECONDARY};
}}
#logLineError {{
    color: {ERROR_TEXT};
}}
#btnDownloadLog {{
    font-size: 11px;
    color: {GREEN};
    background: transparent;
    border: none;
    padding: 0;
    font-weight: 600;
}}
#btnDownloadLog:hover {{
    text-decoration: underline;
}}

/* ---- Empty queue state ---- */
#emptyQueueLabel {{
    font-size: 13px;
    color: {INK_400};
}}
#emptyQueueSub {{
    font-size: 12px;
    color: {INK_400};
}}
"""
