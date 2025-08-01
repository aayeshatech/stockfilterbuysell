"""
Advanced Astro Trading Dashboard with Dynamic Layout
"""

import streamlit as st
from datetime import datetime, timedelta
import pytz
import time
import logging
import yfinance as yf
import ephem
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List, Tuple
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== SYMBOL CONFIGURATION ==================
# Load symbols from provided files
FUTURE_SYMBOLS = [
    "NSE:TRENT1!", "NSE:EICHERMOT1!", "NSE:TVSMOTOR1!", "NSE:AMBUJACEM1!", 
    "NSE:MARICO1!", "NSE:DABUR1!", "NSE:ITC1!", "NSE:ASIANPAINT1!", 
    "NSE:NESTLEIND1!", "NSE:BRITANNIA1!", "NSE:HINDUNILVR1!", 
    "NSE:HEROMOTOCO1!", "NSE:CUMMINSIND1!", "NSE:SBICARD1!", 
    "NSE:GODREJCP1!", "NSE:BAJAJ_AUTO1!", "NSE:KOTAKBANK1!", 
    "NSE:VEDL1!", "NSE:RELIANCE1!", "NSE:NMDC1!", "NSE:AUBANK1!", 
    "NSE:ASTRAL1!", "NSE:CDSL1!", "NSE:DLF1!", "NSE:COLPAL1!", 
    "NSE:BAJFINANCE1!", "NSE:MUTHOOTFIN1!", "NSE:BANKNIFTY1!", 
    "NSE:VOLTAS1!", "NSE:AXISBANK1!", "NSE:TATACONSUM1!", 
    "NSE:RECLTD1!", "NSE:HDFCBANK1!", "NSE:BSE1!", "NSE:NIFTY1!", 
    "NSE:HDFCAMC1!", "NSE:PIDILITIND1!", "NSE:SBIN1!", 
    "NSE:BANKBARODA1!", "NSE:GODREJPROP1!", "NSE:SIEMENS1!", 
    "NSE:CONCOR1!", "NSE:BAJAJFINSV1!", "NSE:TITAN1!", 
    "NSE:HAVELLS1!", "NSE:CANBK1!", "NSE:ANGELONE1!", 
    "NSE:GRASIM1!", "NSE:ASHOKLEY1!", "NSE:PFC1!", 
    "NSE:ICICIBANK1!", "NSE:IRCTC1!", "NSE:BHARTIARTL1!", 
    "NSE:SRF1!", "NSE:DALBHARAT1!", "NSE:BEL1!", 
    "NSE:POLYCAB1!", "NSE:DMART1!", "NSE:INDUSINDBK1!", 
    "NSE:HINDALCO1!", "NSE:ABB1!", "NSE:TCS1!", 
    "NSE:M&M1!", "NSE:PNB1!", "NSE:ULTRACEMCO1!", 
    "NSE:JINDALSTEL1!", "NSE:LT1!", "NSE:COFORGE1!", 
    "NSE:HCLTECH1!", "NSE:COALINDIA1!", "NSE:NAUKRI1!", 
    "NSE:MARUTI1!", "NSE:BHARATFORG1!", "NSE:INDIGO1!", 
    "NSE:SYNGENE1!", "NSE:RBLBANK1!", "NSE:BIOCON1!", 
    "NSE:APOLLOHOSP1!", "NSE:HAL1!", "NSE:UPL1!", 
    "NSE:LICHSGFIN1!", "NSE:MFSL1!", "NSE:ADANIENT1!", 
    "NSE:TATAPOWER1!", "NSE:TECHM1!", "NSE:TORNTPHARM1!", 
    "NSE:HINDZINC1!", "NSE:LTIM1!", "NSE:JUBLFOOD1!", 
    "NSE:HDFCLIFE1!", "NSE:ONGC1!", "NSE:JSWSTEEL1!", 
    "NSE:SBILIFE1!", "NSE:IGL1!", "NSE:BANDHANBNK1!", 
    "NSE:TATAMOTORS1!", "NSE:TATACHEM1!", "NSE:SAIL1!", 
    "NSE:HINDPETRO1!", "NSE:PETRONET1!", "NSE:WIPRO1!", 
    "NSE:INFY1!", "NSE:ICICIPRULI1!", "NSE:ALKEM1!", 
    "NSE:BPCL1!", "NSE:LUPIN1!", "NSE:DIVISLAB1!", 
    "NSE:ICICIGI1!", "NSE:GLENMARK1!", "NSE:TATASTEEL1!", 
    "NSE:CIPLA1!", "NSE:DRREDDY1!", "NSE:SUNPHARMA1!", 
    "NSE:AUROPHARMA1!", "NSE:PNBHOUSING1!"
]

WATCHLIST_SYMBOLS = [
    "NSE:PNBHOUSING", "NSE:ZUARI", "NSE:GRAPHITE", "NSE:PRAKASH", 
    "NSE:HEG", "NSE:KPRMILL", "NSE:GLAXO", "BSE:AFFORDABLE", 
    "NSE:SONATSOFTW", "NSE:RGL", "BSE:FUNDVISER", "NSE:PTC", 
    "NSE:ARSHIYA", "NSE:COMPINFO", "NSE:PVP", "NSE:WEBELSOLAR", 
    "NSE:RELINFRA", "BSE:HINDBIO", "NSE:SOLARA", "NSE:AUROPHARMA", 
    "NSE:NAVKARCORP", "NSE:INDUSTOWER", "BSE:JCTLTD", "NSE:SUNPHARMA", 
    "NSE:GRANULES", "NSE:SWANENERGY", "NSE:THOMASCOOK", 
    "NSE:JAYNECOIND", "NSE:PEL", "NSE:CHEMCON", "NSE:GLAND", 
    "NSE:LYKALABS", "NSE:GOKUL", "NSE:DRREDDY", "NSE:VALIANTORG", 
    "NSE:ASHAPURMIN", "NSE:SHALPAINTS", "NSE:JPPOWER", "NSE:KRBL", 
    "NSE:JMFINANCIL", "NSE:SWSOLAR", "NSE:PENINLAND", "BSE:GUJTHEM", 
    "NSE:AMBIKCO", "NSE:INTELLECT", "BSE:MARSONS", "BSE:ASMTEC", 
    "NSE:HIMATSEIDE", "NSE:CIPLA", "NSE:DECCANCE", "BSE:INTEGRAEN", 
    "NSE:LXCHEM", "NSE:IDEA", "NSE:JAICORPLTD", "NSE:EDELWEISS", 
    "NSE:GLENMARK", "NSE:GREENPANEL", "NSE:STAR", "NSE:AXISCADES", 
    "NSE:MUNJALSHOW", "NSE:SPANDANA", "NSE:BPCL", "NSE:BASF", 
    "NSE:GREAVESCOT", "NSE:JUBLINGREA", "NSE:HTMEDIA", 
    "NSE:CHENNPETRO", "NSE:BALRAMCHIN", "NSE:SHILPAMED", 
    "NSE:ICIL", "NSE:MSPL", "NSE:SBFC", "NSE:TATASTEEL", 
    "NSE:HINDPETRO", "NSE:VTL", "NSE:SAIL", "NSE:NEWGEN", 
    "NSE:RELIGARE", "NSE:HARIOMPIPE", "NSE:RUBYMILLS", 
    "NSE:LAURUSLABS", "NSE:ENGINERSIN", "NSE:BFUTILITIE", 
    "NSE:JHS", "NSE:MARATHON", "NSE:DIVISLAB", "NSE:NLCINDIA", 
    "BSE:KRRAIL", "NSE:GENESYS", "NSE:LUPIN", "NSE:BAJAJHCARE", 
    "NSE:BOMDYEING", "NSE:ASTRAZEN", "NSE:DCAL", "NSE:RKFORGE", 
    "BSE:ZUARIIND", "NSE:GUJGASLTD", "NSE:RAILTEL", "NSE:CLSEL", 
    "NSE:BHEL", "NSE:TALBROAUTO", "NSE:SPORTKING", "NSE:EVEREADY", 
    "NSE:AARTIIND", "BSE:BMW", "NSE:PPLPHARMA", "NSE:STOVEKRAFT", 
    "NSE:FEDERALBNK", "NSE:TFCILTD", "NSE:GMDCLTD", "NSE:MAHABANK", 
    "NSE:NFL", "NSE:CNXPHARMA/NSE:NIFTY", "NSE:SENORES", 
    "NSE:TIMETECHNO", "NSE:AARTIDRUGS", "NSE:STLTECH", 
    "NSE:EPIGRAL", "NSE:USHAMART", "NSE:AVANTIFEED", "NSE:CENTUM", 
    "NSE:ABSLAMC", "BSE:SUCROSA", "NSE:WELCORP", "NSE:ADANIPOWER", 
    "NSE:PRITIKAUTO", "NSE:RCF", "NSE:ICICIPRULI", "NSE:COCHINSHIP", 
    "NSE:MIRCELECTR", "NSE:RPSGVENT", "NSE:HERANBA", "NSE:NOCIL", 
    "NSE:TMB", "NSE:MEP", "NSE:ALKEM", "NSE:HFCL", "NSE:BEML", 
    "NSE:FINPIPE", "NSE:FMGOETZE", "NSE:PLATIND", "NSE:TATACHEM", 
    "NSE:EMBDL", "NSE:BIRLACORPN", "NSE:3IINFOLTD", "NSE:TAC", 
    "NSE:AGARIND", "NSE:GAYAPROJ", "NSE:MTARTECH", "NSE:CENTEXT", 
    "NSE:IOLCP", "NSE:DUCON", "NSE:NATIONALUM", "NSE:GICRE", 
    "NSE:PRECAM", "NSE:PARAGMILK", "NSE:MEDPLUS", "NSE:SBILIFE", 
    "NSE:WIPRO", "NSE:STANLEY", "NSE:ZYDUSLIFE", "NSE:SCI", 
    "NSE:SAKHTISUG", "NSE:MAHLOG", "NSE:DEEPAKFERT", "BSE:WIMPLAST", 
    "NSE:JINDALSAW", "BSE:VIKASWSP", "NSE:JUBLPHARMA", "NSE:GESHIP", 
    "NSE:PURVA", "NSE:SCHAND", "NSE:PRSMJOHNSN", "NSE:DBREALTY", 
    "NSE:LODHA", "NSE:IDBI", "NSE:MARUTI", "NSE:WOCKPHARMA", 
    "NSE:RALLIS", "NSE:LICHSGFIN", "NSE:TNPETRO", "NSE:OBEROIRLTY", 
    "NSE:GSPL", "NSE:IEX", "NSE:RAIN", "NSE:ENRIN", 
    "NSE:CEREBRAINT", "NSE:GPIL", "NSE:BBL", "NSE:ABB", 
    "NSE:WSTCSTPAPR", "NSE:CEATLTD", "NSE:TATAPOWER", 
    "NSE:SARDAEN", "NSE:MFSL", "NSE:INDIGO", "NSE:UTIAMC", 
    "NSE:UNICHEMLAB", "NSE:ABCAPITAL", "NSE:APOLLOHOSP", 
    "NSE:INDIACEM", "NSE:CESC", "NSE:STARHEALTH", "NSE:SHARDACROP", 
    "NSE:UJJIVANSFB", "NSE:MOIL", "NSE:INDUSINDBK", "NSE:APOLLOTYRE", 
    "BSE:ASIANENE", "NSE:JBCHEPHARM", "NSE:POLICYBZR", "NSE:GAIL", 
    "NSE:AJANTPHARM", "NSE:SYMPHONY", "NSE:POLYPLEX", 
    "NSE:GREENPOWER", "NSE:GSFC", "NSE:NECCLTD", "NSE:MANALIPETC", 
    "NSE:SPCENET", "NSE:REPRO", "NSE:PNB", "NSE:NAUKRI", 
    "BSE:ASHCAP", "BSE:ANDHRAPET", "NSE:NATCOPHARM", "NSE:RAMCOCEM", 
    "BSE:MHLXMIRU", "NSE:CNXMETAL", "XETR:DAX", "NSE:BIOCON", 
    "NSE:GULPOLY", "NSE:BEDMUTHA", "NSE:PITTIENG", "NSE:ONGC", 
    "NSE:MINDACORP", "NSE:BGRENERGY", "NSE:HINDZINC", "NSE:APOLLO", 
    "NSE:APLLTD", "NSE:ARKADE", "NSE:GANESHBE", "NSE:SEQUENT", 
    "NSE:BLISSGVS", "NSE:PARSVNATH", "NSE:DELTACORP", "NSE:BANKINDIA", 
    "NSE:CNXIT", "NSE:ABAN", "NSE:EKC", "NSE:UNIONBANK", 
    "NSE:MGL", "NSE:ESCORTS", "BSE:BOMOXY_B1", "NSE:WALCHANNAG", 
    "NSE:LEMONTREE", "NSE:MOTHERSON", "NSE:DMART", "NSE:SYNGENE", 
    "NSE:TNPL", "NSE:TORNTPOWER", "NSE:IDFCFIRSTB", "NSE:ROSSARI", 
    "NSE:DALBHARAT", "FX:GER30", "NSE:ALLCARGO", "NSE:TORNTPHARM", 
    "NSE:DHANI", "NSE:JKTYRE", "NSE:IGL", "NSE:UCOBANK", 
    "BSE:TITANSEC", "NSE:BHARTIARTL", "NSE:BAJAJHIND", "NSE:BETA", 
    "NSE:MAZDOCK", "NSE:HINDOILEXP", "NSE:NIFTYSMLCAP50", 
    "NSE:GUJALKALI", "NSE:ADANIENSOL", "NSE:HMT", "NSE:AWL", 
    "NSE:ZIMLAB", "NSE:CERA", "NSE:SAKSOFT", "BSE:SAURASHCEM", 
    "BINANCE:LTCUSD", "NSE:LTFOODS", "NSE:SUNDARAM", "NSE:NAM_INDIA", 
    "NSE:MANAPPURAM", "NSE:INDIAGLYCO", "NSE:KARURVYSYA", 
    "NSE:HLEGLAS", "NSE:SAREGAMA", "NSE:RITES", "NSE:MRPL", 
    "NSE:CENTRUM", "NSE:OMINFRAL", "NSE:KPITTECH", "NSE:CHOLAFIN", 
    "NSE:NESCO", "NSE:YESBANK", "NSE:CNXSMALLCAP", "NSE:RAYMOND", 
    "NSE:WABAG", "NSE:CAPACITE", "NSE:ANDHRSUGAR", "NSE:TRACXN", 
    "NSE:CNXPSE", "NSE:NIFTYSMLCAP250", "NSE:VINYLINDIA", 
    "NSE:HARRMALAYA", "NSE:DWARKESH", "NSE:WINDMACHIN", 
    "NSE:HILTON", "NSE:TRF", "NSE:POONAWALLA", "NSE:MSTCLTD", 
    "NSE:HLVLTD", "NSE:URJA", "NSE:RELAXO", "NSE:COFFEEDAY", 
    "NSE:FORCEMOT", "HKEX:HSI1!", "NSE:JYOTISTRUC", "NSE:JUSTDIAL", 
    "NSE:LAMBODHARA", "NSE:MARKSANS", "BSE:SABOOSOD", "NSE:OIL", 
    "NSE:CNXMETAL/NSE:NIFTY", "NSE:BAJAJFINSV", "NSE:JWL", 
    "NSE:HIKAL", "NSE:SIS", "NSE:GRSE", "NSE:DEEPAKNTR", 
    "NSE:CANFINHOME", "BSE:MINALIND", "BSE:ANDREWYU", "NSE:ASTERDM", 
    "NSE:SAGCEM", "NSE:IPCALAB", "NSE:ELGIEQUIP", "NSE:CENTRALBK", 
    "BSE:ORISSAMINE", "BSE:VRFILMS", "NSE:PAYTM", "NSE:LT", 
    "NSE:ZENSARTECH", "NSE:LICI", "NSE:ENIL", "NSE:IMAGICAA", 
    "FX:NAS100", "NSE:PAISALO", "NSE:KOPRAN", "NSE:LIBERTSHOE", 
    "BSE:SGFIN", "NSE:AMBER", "NSE:STEL", "NSE:SOBHA", 
    "NSE:TEJASNET", "NSE:OLAELEC", "NSE:MANINFRA", "NSE:ALOKINDS", 
    "NSE:KTKBANK", "NSE:KAKATCEM", "FX:SPX500", "BSE:ANUHPHR", 
    "NSE:ARIES", "NSE:VOLTAS", "NSE:HCG", "NSE:SUVEN", 
    "NSE:SPENCERS", "NSE:MOREPENLAB", "NSE:LOVABLE", "NSE:GNFC", 
    "TVC:USOIL", "NSE:GLOBALVECT", "NSE:IRCTC", "NSE:SELAN", 
    "NSE:ELECON", "NSE:RTNINDIA", "NSE:ROSSELLIND", "NSE:SHALBY", 
    "NSE:XPROINDIA", "NSE:HEMIPROP", "NSE:TATATECH", "NSE:HCLTECH", 
    "NSE:RAMCOSYS", "NSE:COALINDIA", "NSE:UFLEX", "BSE:SHIVACEM", 
    "AMEX:DIA", "NSE:APARINDS", "NSE:PDSL", "NSE:PSPPROJECT", 
    "NSE:ASTRAMICRO", "NSE:BAJAJHFL", "NSE:TEXINFRA", "BSE:HFIL", 
    "NSE:NEULANDLAB", "FX:UKOIL", "NSE:HATSUN", "NSE:ALBERTDAVD", 
    "NSE:NSLNISP", "NSE:DISHTV", "NSE:JAMNAAUTO", "NSE:DIAMONDYD", 
    "NSE:RAMASTEEL", "NSE:RVNL", "NSE:VAIBHAVGBL", "NSE:FSL", 
    "NYMEX:CL1!", "NSE:GRASIM", "NSE:DBCORP", "NSE:JSWENERGY", 
    "NSE:ATGL", "NSE:NECLIFE", "NSE:CUB", "NSE:HEIDELBERG", 
    "NSE:NAVINFLUOR", "NSE:TCI", "NSE:GTLINFRA", "NSE:HUDCO", 
    "NSE:BYKE", "NSE:MCX", "FX:JPN225", "NSE:GULFPETRO", 
    "NSE:JTLIND", "NSE:SUBEXLTD", "NSE:VASCONEQ", "NSE:TATAELXSI", 
    "NSE:ALPHAGEO", "NSE:DLINKINDIA", "NSE:DREDGECORP", "FX:GBPJPY", 
    "NSE:DTIL", "NSE:SPECIALITY", "NSE:DOLATALGO", "NSE:RADIOCITY", 
    "NSE:ORISSAMINE", "BSE:GOODRICKE", "NSE:VISHWARAJ", 
    "NSE:ADANIGREEN", "NSE:ICICIBANK", "NSE:VPRPL", "NSE:NBCC", 
    "NSE:JAYAGROGN", "NSE:STARPAPER", "NSE:HAPPSTMNDS", 
    "NSE:NITINSPIN", "NSE:HERITGFOOD", "NSE:INSPIRISYS", 
    "NSE:RANASUG", "NSE:SHYAMMETL", "NSE:WHIRLPOOL", "BSE:COCKERILL", 
    "NSE:PATELENG", "NSE:ASIANTILES", "NSE:CNXMIDCAP/NSE:NIFTY", 
    "NSE:LUXIND", "NSE:MGEL", "NSE:ASHOKLEY", "NSE:SCHAEFFLER", 
    "NSE:NIFTYPVTBANK", "NSE:VSTTILLERS", "NSE:KEI", "NSE:VIKASLIFE", 
    "NSE:TTML", "NSEIX:NIFTY1!", "NSE:BSE", "NSE:NAZARA", 
    "NSE:GOLDBEES", "NSE:ANMOL", "FX_IDC:GBPUSD", "NSE:KOLTEPATIL", 
    "NSE:CNXENERGY", "NSE:CONCOR", "AMEX:SPY", "NSE:KNRCON", 
    "NSE:KCPSUGIND", "TVC:SPX", "NSE:PGINVIT", "INDEX:SENSEX", 
    "NSE:TANLA", "NSE:BPL", "NSE:CMSINFO", "NSE:SBIN", "FX:UK100", 
    "NSE:SUNTV", "NSE:HERCULES", "BSE:PROTEAN", "NSE:THYROCARE", 
    "NSE:CROMPTON", "BSE:RNBDENIMS", "NSE:SBICARD", "NSE:AXISBANK", 
    "BSE:SVCIND", "NSE:RUPA", "NSE:AVADHSUGAR", "NSE:CNXAUTO/NSE:NIFTY", 
    "MCX:NATURALGAS1!", "NSE:INDTERRAIN", "NSE:PIDILITIND", 
    "NSE:VENKEYS", "NSE:POCL", "NSE:KHAICHEM", "NSE:DCW", 
    "BSE:ZFSTEERING", "NSE:MUTHOOTFIN", "NSE:CDSL", "MCX:GOLDM1!", 
    "BSE:VERITAS", "NSE:JSWINFRA", "NSE:HDFCBANK", "BSE:BAJAJHLDNG", 
    "AMEX:FXE", "NSE:TATACONSUM", "NSE:SEPC", "COMEX:GC1!", 
    "FX:EURUSD", "NSE:ORIENTPPR", "NSE:IGPL", "NSE:MAHASTEEL", 
    "NSE:ANANTRAJ", "BSE:VOEPL", "NSE:BAJFINANCE", "NSE:ARCHIDPLY", 
    "NSE:LGBBROSLTD", "NSE:EMAMIREAL", "NSE:LRRPL", "BSE:NOL", 
    "BSE:GVFILM", "NSE:HCC", "NSE:RENUKA", "BSE:TOYAMSL", 
    "BSE:ORCHASP", "NSE:MAXHEALTH", "NSE:PRINCEPIPE", 
    "NSE:KOTARISUG", "NSE:VEDL", "NSE:JAGRAN", "NSE:ORIENTELEC", 
    "TVC:US10Y", "ICEUS:SB1!", "NSE:SHANKARA", "BSE:STML", 
    "OANDA:XAUUSD/TVC:US10Y", "NSE:ATULAUTO", "NSE:KANORICHEM", 
    "NSE:MCLEODRUSS", "NSE:MTNL", "NSE:SATIN", "NSE:MEDICAMEQ", 
    "TVC:DXY", "NSE:KCP", "NSE:DIXON", "BSE:AMNPLST", "NSE:VESUVIUS", 
    "NSE:KUANTUM", "NSE:AMJLAND", "BSE:RDBRL", "NSE:BANKNIFTY/NSE:NIFTY", 
    "NSE:NYKAA", "NSE:BANG", "NSE:OCCL", "NSE:INDIAMART", 
    "NSE:ANURAS", "NSE:RTNPOWER", "NSE:JKLAKSHMI", "NSE:JIOFIN", 
    "BSE:DECNGOLD", "NSE:SPARC", "BSE:ISGEC", "NSE:DIACABS", 
    "NSE:SAMMAANCAP", "NSE:TATAINVEST", "NSE:TTKPRESTIG", 
    "BSE:UGROCAP", "NSE:BLAL", "NSE:MODIRUBBER", "BSE:GSTL", 
    "NSE:SADBHAV", "NSE:GEPIL", "NSE:MONTECARLO", "NSE:POLYMED", 
    "NSE:BHAGERIA", "INDEX:BDI", "NSE:HATHWAY", "NSE:EASEMYTRIP", 
    "FX_IDC:USDGBP", "NSE:PNCINFRA", "BSE:CHEMCRUX", "MCX:NICKEL1!", 
    "NSE:NIFTYPVTBANK/NSE:CNXPSUBANK", "NSE:CASTROLIND", 
    "NSE:PANACEABIO", "NSE:M&MFIN", "NSE:NIFTY/NSE:CNXMIDCAP", 
    "NSE:AFFLE", "NSE:NAGAFERT", "NSE:AURIONPRO", "NSE:BAJAJ_AUTO", 
    "NSE:PRAJIND", "NSE:COLPAL", "NSE:HEADSUP", "NSE:BBTC", 
    "NSE:RUCHINFRA", "NSE:BERGEPAINT", "NSE:HINDMOTORS", 
    "NSE:IFBIND", "NSE:PVRINOX", "NSE:CSBBANK", "NSE:TOKYOPLAST", 
    "AMEX:GLD", "NSE:INVENTURE", "NSE:KOTAKBANK", "NSE:GICHSGFIN", 
    "NSE:LALPATHLAB", "NSE:INDIANB", "NSE:BLS", "OANDA:XAUUSD/OANDA:XAGUSD", 
    "NSE:RSYSTEMS", "NSE:RPTECH", "NSE:BORORENEW", "NSE:IEL", 
    "NSE:JKCEMENT", "NSE:ANNAPURNA", "BSE:AMAL", "NSE:BRITANNIA", 
    "NSE:GODREJCP", "NSE:VETO", "NSE:CAMPUS", "NSE:INOXWIND", 
    "NSE:CHAMBLFERT", "NSE:VIPIND", "NSE:SECURKLOUD", "NSE:KIMS", 
    "BSE:GENPHARMA", "BSE:M_MFIN", "NSE:SURYODAY", "NSE:KAYA", 
    "NSE:HEROMOTOCO", "NSE:STYLAMIND", "BSE:LOTUSCHO", "NSE:IFCI", 
    "NSE:ECLERX", "NSE:DABUR", "NSE:BAJAJCON", "NSE:PARADEEP", 
    "BSE:MANGIND", "NSE:20MICRONS", "NSE:ACCELYA", "NSE:IGARASHI", 
    "NSE:MOTILALOFS", "NSE:SAMHI", "NSE:NESTLEIND", "NSE:ABFRL", 
    "NSE:HINDUNILVR", "NSE:JSL", "NSE:ASIANPAINT", "NSE:DEN", 
    "BSE:DEEPAKSP", "NSE:MASTEK", "BSE:PPL", "NSE:KANSAINER", 
    "NSE:SASTASUNDR", "BSE:BALUFORGE", "BSE:GGENG", "NSE:AGSTRA", 
    "NSE:KESORAMIND", "NSE:JAYSREETEA", "NSE:MEDANTA", "NSE:VENUSREM", 
    "NSE:BROOKS", "NSE:SKMEGGPROD", "NSE:DCBBANK", "NSE:METROPOLIS", 
    "NSE:PCBL", "BSE:MENNPIS", "BSE:FACORALL", "NSE:DIGISPICE", 
    "NSE:GENUSPOWER", "BSE:INVPRECQ", "NSE:INDIAVIX", 
    "NSE:NIFTY/NSE:CNXPHARMA", "NSE:SHRIRAMPPS", "NSE:ADVENZYMES", 
    "NSE:OLECTRA", "NSE:TI", "NSE:APTUS", "NSE:EMAMILTD", 
    "NSE:KAYNES", "NSE:TRENT", "BSE:KESARPE", "NSE:MMTC", 
    "BSE:RIDDHICORP", "NSE:EROSMEDIA", "NSE:JPASSOCIAT", 
    "NSE:BALAJITELE", "NSE:SMLISUZU", "NSE:PDMJEPAPER", "NSE:CCL", 
    "NSE:NETWEB", "NSE:DIGIDRIVE", "NSE:SUZLON", "BSE:ARFIN", 
    "TVC:VIX"
]

EYE_SYMBOLS_LIST = [
    "MCX:ALUMINIUM1!", "NSE:BANKNIFTY", "BITSTAMP:BTCUSD", 
    "NSE:CNX100", "NSE:CNX200", "NSE:CNXAUTO", "NSE:CNXCOMMODITIES", 
    "NSE:CNXCONSUMPTION", "NSE:CNXENERGY", "NSE:CNXFINANCE", 
    "NSE:CNXFMCG", "NSE:CNXINFRA", "NSE:CNXIT", "NSE:CNXMEDIA", 
    "NSE:CNXMETAL", "NSE:CNXMIDCAP", "NSE:CNXMNC", "NSE:CNXPHARMA", 
    "NSE:CNXPSE", "NSE:CNXPSUBANK", "NSE:CNXREALTY", 
    "NSE:CNXSMALLCAP", "MCX:COPPER1!", "MCX:CRUDEOIL1!", 
    "BSE:DRONACHRYA", "CAPITALCOM:DXY", "COINBASE:ETHUSD", 
    "BITSTAMP:ETHUSD", "NSE:FINNIFTY1!", "COMEX:GC1!", "MCX:GOLD1!", 
    "NSE:INDIAVIX", "NSE:INTERARCH", "NSE:NIFTY", 
    "NSE:NIFTY/CAPITALCOM:DXY", "NSEIX:NIFTY1!", "NSE:NIFTYJR", 
    "NSE:NIFTYMIDCAP50", "NSE:NIFTYSMLCAP250", "NSE:NIFTYSMLCAP50", 
    "NSE:NIFTY_OIL_AND_GAS", "MCX:SILVER1!", "OANDA:SUGARUSD", 
    "TASE:TA35", "FX:UKOIL", "CFI:US100", "TVC:US10Y", "FX:US30", 
    "CAPITALCOM:US500", "FX_IDC:USDINR", "FX:USOIL", "OANDA:XAGUSD", 
    "BIST:XAGUSD1!", "OANDA:XAUUSD", "FX:XAUUSD"
]

# Combine all symbols
ALL_SYMBOLS = list(set(FUTURE_SYMBOLS + WATCHLIST_SYMBOLS + EYE_SYMBOLS_LIST))

# Enhanced planet mapping
PLANET_MAPPING = {
    # Commodities
    "GOLD": "Sun", "SILVER": "Moon", "CRUDEOIL": "Mars", 
    "NATURALGAS": "Venus", "ALUMINIUM": "Mercury", "COPPER": "Venus",
    "SUGAR": "Jupiter", "OIL": "Neptune",
    
    # Major Indices
    "NIFTY": "Jupiter", "BANKNIFTY": "Mercury", "SENSEX": "Sun",
    "FINNIFTY": "Mercury", "MIDCAP": "Venus", "SMALLCAP": "Mars",
    
    # Sectors
    "AUTO": "Mars", "IT": "Mercury", "PHARMA": "Moon", 
    "FMCG": "Venus", "BANK": "Mercury", "FINANCE": "Jupiter",
    "METAL": "Mars", "ENERGY": "Sun", "REALTY": "Venus",
    
    # Crypto
    "BTC": "Uranus", "ETH": "Neptune", "SOL": "Pluto",
    
    # Major Stocks
    "RELIANCE": "Jupiter", "TATA": "Venus", "HDFC": "Mercury",
    "INFY": "Saturn", "ICICI": "Neptune", "BHARTI": "Mars",
    "TCS": "Mercury", "WIPRO": "Mercury", "HINDUNILVR": "Venus",
    "ITC": "Venus", "ASIANPAINT": "Venus", "NESTLE": "Moon",
    
    # Default
    "DEFAULT": "Sun"
}

# Eye symbol mapping
EYE_SYMBOLS = {
    "STRONG_BUY": "👁️🟢✨", 
    "BUY": "👁️🟢",
    "STRONG_SELL": "👁️🔴✨",
    "SELL": "👁️🔴", 
    "HOLD": "👁️⚪",
    "WARNING": "👁️🟡"
}

# ================== OPTIMIZED FUNCTIONS ==================
@st.cache_data(ttl=60, show_spinner=False)
def get_live_price(symbol: str) -> float:
    """Cached price fetch with enhanced error handling"""
    try:
        clean_symbol = symbol.split(":")[-1].split("-")[0].split("/")[0].replace("^", "")
        data = yf.Ticker(clean_symbol).history(period="1d", interval="1m", timeout=5)
        return data["Close"].iloc[-1] if not data.empty else 0.0
    except Exception as e:
        logger.warning(f"Price fetch failed for {symbol}: {str(e)}")
        return 0.0

@lru_cache(maxsize=512)
def get_planet_strength(planet: str, timestamp: float) -> Tuple[float, str, str]:
    """Enhanced planetary strength with transit info"""
    try:
        now = datetime.fromtimestamp(timestamp, pytz.utc)
        planet_obj = getattr(ephem, planet)()
        observer = ephem.Observer()
        observer.date = now
        planet_obj.compute(observer)
        
        # Calculate current strength (0-1 scale)
        current_strength = float(planet_obj.alt / (ephem.pi/2))
        
        # Calculate next significant transit
        next_transit = observer.next_transit(planet_obj)
        transit_time = ephem.localtime(next_transit).strftime("%H:%M UTC")
        
        # Calculate previous transit
        prev_transit = observer.previous_transit(planet_obj)
        prev_transit_time = ephem.localtime(prev_transit).strftime("%H:%M UTC")
        
        return current_strength, transit_time, prev_transit_time
    except Exception as e:
        logger.warning(f"Planet calc error for {planet}: {str(e)}")
        return 0.5, "N/A", "N/A"

def get_planet(symbol: str) -> str:
    """Enhanced symbol-to-planet mapping with sector detection"""
    symbol_upper = symbol.upper()
    
    # Check for exact matches first
    for key, planet in PLANET_MAPPING.items():
        if key in symbol_upper:
            return planet
            
    # Check for sector keywords
    if any(x in symbol_upper for x in ["BANK", "FIN"]):
        return PLANET_MAPPING["BANK"]
    if "PHARMA" in symbol_upper or any(x in symbol_upper for x in ["DRUG", "MED", "HEALTH"]):
        return PLANET_MAPPING["PHARMA"]
    if "IT" in symbol_upper or "TECH" in symbol_upper:
        return PLANET_MAPPING["IT"]
    if "AUTO" in symbol_upper or "MOTOR" in symbol_upper:
        return PLANET_MAPPING["AUTO"]
    if "OIL" in symbol_upper or "GAS" in symbol_upper:
        return PLANET_MAPPING["ENERGY"]
    if "METAL" in symbol_upper or "STEEL" in symbol_upper:
        return PLANET_MAPPING["METAL"]
    if "FMCG" in symbol_upper or "CONSUM" in symbol_upper:
        return PLANET_MAPPING["FMCG"]
    
    # Default based on symbol characteristics
    if any(x in symbol_upper for x in ["GOLD", "SUN", "LIGHT"]):
        return "Sun"
    if any(x in symbol_upper for x in ["SILVER", "MOON", "WATER"]):
        return "Moon"
    if any(x in symbol_upper for x in ["OIL", "FIRE", "ENERGY"]):
        return "Mars"
    if any(x in symbol_upper for x in ["LOVE", "BEAUTY", "ART"]):
        return "Venus"
    if any(x in symbol_upper for x in ["COMM", "TECH", "MERC"]):
        return "Mercury"
    if any(x in symbol_upper for x in ["GROWTH", "LUCK", "EXPAN"]):
        return "Jupiter"
        
    return PLANET_MAPPING["DEFAULT"]

def get_transit_alert(planet: str, transit_time: str, prev_transit: str) -> str:
    """Generate transit alert message with timing info"""
    alerts = {
        "Sun": "Solar peak at {next} (prev: {prev})",
        "Moon": "Lunar shift at {next} (prev: {prev})",
        "Mercury": "Mercury transit at {next} (prev: {prev})",
        "Venus": "Venus alignment at {next} (prev: {prev})",
        "Mars": "Mars energy at {next} (prev: {prev})",
        "Jupiter": "Jupiter expansion at {next} (prev: {prev})",
        "Saturn": "Saturn restriction at {next} (prev: {prev})",
        "Uranus": "Uranus disruption at {next} (prev: {prev})",
        "Neptune": "Neptune intuition at {next} (prev: {prev})",
        "Pluto": "Pluto transformation at {next} (prev: {prev})"
    }
    return alerts.get(planet, "Planetary transit at {next} (prev: {prev})").format(
        next=transit_time, prev=prev_transit
    )

def calculate_signal(strength: float, planet: str) -> Tuple[str, str]:
    """Enhanced signal logic with planetary influences"""
    # Base thresholds
    if strength > 0.85:
        return "STRONG_BUY", "Extremely favorable planetary alignment"
    elif strength > 0.7:
        return "BUY", "Strong planetary support"
    elif strength < 0.15:
        return "STRONG_SELL", "Critical planetary opposition"
    elif strength < 0.3:
        return "SELL", "Challenging planetary aspects"
    
    # Planetary-specific adjustments
    if planet == "Mercury" and 0.4 < strength < 0.6:
        return "WARNING", "Mercury neutral - potential volatility"
    if planet == "Mars" and strength > 0.6:
        return "BUY", "Mars energy driving momentum"
    if planet == "Saturn" and strength < 0.4:
        return "SELL", "Saturn restriction in effect"
    
    return "HOLD", "Neutral planetary influence"

def fetch_all_data(symbols: List[str], now: datetime) -> List[Dict]:
    """Parallel data fetching with enhanced info"""
    timestamp = now.timestamp()
    
    def process_symbol(symbol):
        planet = get_planet(symbol)
        strength, next_transit, prev_transit = get_planet_strength(planet, timestamp)
        price = get_live_price(symbol)
        
        signal, reason = calculate_signal(strength, planet)
        
        return {
            "Symbol": symbol,
            "Price": f"{price:,.2f}" if price > 0 else "N/A",
            "Signal": signal,
            "Signal_Display": f"{EYE_SYMBOLS.get(signal, '👁️⚪')} {signal.replace('_', ' ')}",
            "Reason": reason,
            "Confidence": f"{strength:.0%}",
            "Planet": planet,
            "Transit": get_transit_alert(planet, next_transit, prev_transit),
            "Next_Transit": next_transit,
            "Color": "darkgreen" if "STRONG_BUY" in signal 
                     else "green" if "BUY" in signal 
                     else "darkred" if "STRONG_SELL" in signal 
                     else "red" if "SELL" in signal 
                     else "orange" if "WARNING" in signal 
                     else "gray",
            "Strength": strength,
            "Planet_Emoji": {
                "Sun": "☀️", "Moon": "🌙", "Mercury": "☿", 
                "Venus": "♀", "Mars": "♂", "Jupiter": "♃",
                "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
                "Pluto": "♇"
            }.get(planet, "🪐")
        }
    
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(process_symbol, symbols))
        return sorted(results, key=lambda x: x["Strength"], reverse=True)

# ================== DYNAMIC STREAMLIT UI ==================
def main():
    st.set_page_config(
        page_title="Astro Trading Pro",
        layout="wide",
        page_icon="🔮",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better visuals
    st.markdown("""
    <style>
        .st-emotion-cache-1kyxreq {
            display: flex;
            flex-flow: wrap;
            gap: 1rem;
        }
        .symbol-card {
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .symbol-card:hover {
            transform: translateY(-5px);
        }
        .signal-strong-buy {
            background: linear-gradient(135deg, #e6ffe6, #ccffcc);
            border-left: 5px solid #00cc00;
        }
        .signal-buy {
            background: linear-gradient(135deg, #f0fff0, #e0ffe0);
            border-left: 5px solid #00aa00;
        }
        .signal-strong-sell {
            background: linear-gradient(135deg, #ffe6e6, #ffcccc);
            border-left: 5px solid #cc0000;
        }
        .signal-sell {
            background: linear-gradient(135deg, #fff0f0, #ffe0e0);
            border-left: 5px solid #aa0000;
        }
        .signal-warning {
            background: linear-gradient(135deg, #fff9e6, #fff2cc);
            border-left: 5px solid #ffaa00;
        }
        .signal-hold {
            background: linear-gradient(135deg, #f5f5f5, #e5e5e5);
            border-left: 5px solid #888888;
        }
        .planet-indicator {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        .symbol-name {
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 5px;
        }
        .signal-display {
            font-size: 1.3rem;
            font-weight: bold;
            margin: 5px 0;
        }
        .price-display {
            font-size: 1.2rem;
            margin: 5px 0;
        }
        .transit-info {
            font-size: 0.9rem;
            color: #555;
            margin-top: 5px;
        }
        .section-title {
            border-bottom: 2px solid #eee;
            padding-bottom: 5px;
            margin-top: 20px;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.image("https://i.imgur.com/8Km9tLL.png", width=200, use_column_width=True)
        st.title("Astro Trading Controls")
        
        # Symbol selection
        selected_group = st.selectbox(
            "Select Symbol Group",
            ["All Symbols", "Futures", "Watchlist", "Eye Symbols", "Custom Selection"]
        )
        
        if selected_group == "Custom Selection":
            selected_symbols = st.multiselect(
                "Select Symbols",
                ALL_SYMBOLS,
                default=ALL_SYMBOLS[:10]
            )
        else:
            group_map = {
                "All Symbols": ALL_SYMBOLS,
                "Futures": FUTURE_SYMBOLS,
                "Watchlist": WATCHLIST_SYMBOLS,
                "Eye Symbols": EYE_SYMBOLS_LIST
            }
            selected_symbols = group_map[selected_group]
        
        # Display filters
        min_confidence = st.slider(
            "Minimum Confidence Threshold", 
            0, 100, 30, 5,
            help="Filter signals by minimum confidence level"
        )
        
        signal_filter = st.multiselect(
            "Filter Signals",
            ["STRONG_BUY", "BUY", "WARNING", "HOLD", "SELL", "STRONG_SELL"],
            default=["STRONG_BUY", "BUY", "STRONG_SELL", "SELL"],
            help="Select which signals to display"
        )
        
        # Auto-refresh controls
        auto_refresh = st.checkbox("Enable Live Mode", True)
        refresh_rate = st.slider(
            "Refresh Frequency (seconds)", 
            15, 300, 60,
            help="How often to refresh data in live mode"
        )
        
        # Information
        st.markdown("### Signal Guide")
        st.markdown("""
        - 👁️🟢✨ Strong Buy (Very High Confidence)
        - 👁️🟢 Buy (High Confidence)
        - 👁️🟡 Warning (Potential Volatility)
        - 👁️⚪ Hold (Neutral)
        - 👁️🔴 Sell (High Confidence)
        - 👁️🔴✨ Strong Sell (Very High Confidence)
        """)
        
        st.markdown("### Planet Indicators")
        cols = st.columns(3)
        planets = {
            "Sun": "☀️", "Moon": "🌙", "Mercury": "☿", 
            "Venus": "♀", "Mars": "♂", "Jupiter": "♃",
            "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
            "Pluto": "♇"
        }
        for i, (planet, emoji) in enumerate(planets.items()):
            cols[i%3].markdown(f"{emoji} {planet}")
    
    # Main content area
    st.title("🌌 Advanced Astro Trading Dashboard")
    st.caption("Real-time planetary analysis for intraday trading decisions")
    
    # Create placeholder for dynamic content
    placeholder = st.empty()
    
    try:
        while True:
            start_time = time.time()
            now = datetime.now(pytz.utc)
            
            # Fetch data for selected symbols
            with st.spinner("Calculating planetary alignments..."):
                signals = fetch_all_data(selected_symbols, now)
            
            # Filter signals based on user selection
            filtered_signals = [
                s for s in signals 
                if (s["Strength"] >= min_confidence/100) 
                and (s["Signal"] in signal_filter)
            ]
            
            # Group signals by type for better organization
            signal_groups = {
                "STRONG_BUY": [],
                "BUY": [],
                "WARNING": [],
                "HOLD": [],
                "SELL": [],
                "STRONG_SELL": []
            }
            
            for signal in filtered_signals:
                signal_groups[signal["Signal"]].append(signal)
            
            # Display in placeholder
            with placeholder.container():
                # Upcoming transits section
                st.markdown("### 🌠 Upcoming Planetary Transits (Next 24 Hours)")
                transit_cols = st.columns(4)
                transit_counts = {}
                
                for signal in filtered_signals:
                    planet = signal["Planet"]
                    if planet not in transit_counts:
                        transit_counts[planet] = {
                            "count": 0,
                            "transit_time": signal["Next_Transit"],
                            "emoji": signal["Planet_Emoji"]
                        }
                    transit_counts[planet]["count"] += 1
                
                # Display transit cards
                for i, (planet, data) in enumerate(transit_counts.items()):
                    with transit_cols[i % 4]:
                        st.markdown(f"""
                        <div class="symbol-card">
                            <div class="planet-indicator">{data['emoji']}</div>
                            <div>
                                <div><strong>{planet}</strong></div>
                                <div>{data['transit_time']}</div>
                                <div><small>Affects {data['count']} symbols</small></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display signals in groups
                for signal_type, signals_in_group in signal_groups.items():
                    if signals_in_group:
                        st.markdown(f"### {EYE_SYMBOLS.get(signal_type, '👁️⚪')} {signal_type.replace('_', ' ')} Signals ({len(signals_in_group)})")
                        
                        # Create dynamic columns based on number of signals
                        num_cols = min(4, max(2, 6 - len(signals_in_group)//5))
                        cols = st.columns(num_cols)
                        
                        for i, signal in enumerate(signals_in_group):
                            with cols[i % num_cols]:
                                st.markdown(f"""
                                <div class="symbol-card signal-{signal['Signal'].lower().replace('_', '-')}">
                                    <div style="display: flex; align-items: center;">
                                        <div class="planet-indicator">{signal['Planet_Emoji']}</div>
                                        <div class="symbol-name">{signal['Symbol']}</div>
                                    </div>
                                    <div class="signal-display">{signal['Signal_Display']}</div>
                                    <div class="price-display">Price: {signal['Price']}</div>
                                    <div>Confidence: {signal['Confidence']}</div>
                                    <div class="transit-info">{signal['Transit']}</div>
                                    <div><small>{signal['Reason']}</small></div>
                                </div>
                                """, unsafe_allow_html=True)
                
                # Performance metrics
                st.caption(f"""
                Last update: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} | 
                Processed {len(selected_symbols)} symbols in {time.time()-start_time:.2f}s | 
                Showing {len(filtered_signals)} filtered signals
                """)
                
                # Progress bar
                progress_value = min(100, int((time.time() - start_time) * 10))
                st.progress(progress_value, text="System performance")
            
            if not auto_refresh:
                break
            time.sleep(refresh_rate)
    
    except Exception as e:
        logger.error(f"App error: {str(e)}")
        st.error(f"System update needed: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
