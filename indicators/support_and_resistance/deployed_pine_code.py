s = '''
//@version=5
indicator("Support and Resistance - v3 (Enhanced) - {batch_name}", shorttitle="SR {batch_name}", overlay=true)

// ---------------------------------------------------------------------------------------------------------------------
// INPUTS
// ---------------------------------------------------------------------------------------------------------------------
lookbackPeriod = input.int(20)
vol_len        = input.int(2)
box_withd      = input.float(1)

// ---------------------------------------------------------------------------------------------------------------------
// FUNCTIONS
// ---------------------------------------------------------------------------------------------------------------------
upAndDownVolume() =>
    posVol = 0.0
    negVol = 0.0
    var isBuyVolume = true
    switch
        close > open => isBuyVolume := true
        close < open => isBuyVolume := false
    isBuyVolume ? posVol + volume : negVol - volume

getStrike(price, isCE) =>
    step = 50.0
    isCE ? math.floor(price / step) * step : math.ceil(price / step) * step

formatTime(_time) =>
    str.format_time(_time, "yyyy-MM-dd HH:mm", "Asia/Kolkata")

{pine_content}

// ---------------------------------------------------------------------------------------------------------------------
// 🔥 CORE LOGIC (ENHANCED)
// ---------------------------------------------------------------------------------------------------------------------
calcSupportResistance(src) =>
    Vol = upAndDownVolume()
    vol_hi = ta.highest(Vol/2.5, vol_len)
    vol_lo = ta.lowest(Vol/2.5, vol_len)

    var float support = na
    var float resistance = na

    ph = ta.pivothigh(src, lookbackPeriod, lookbackPeriod)
    pl = ta.pivotlow(src, lookbackPeriod, lookbackPeriod)

    if not na(pl) and Vol > vol_hi
        support := pl

    if not na(ph) and Vol < vol_lo
        resistance := ph

    res_holds   = ta.crossunder(high, resistance)
    sup_holds   = ta.crossover(low, support)
    brekout_res = ta.crossover(low, resistance)
    brekout_sup = ta.crossunder(high, support)

    [res_holds, sup_holds, brekout_res, brekout_sup]

// ---------------------------------------------------------------------------------------------------------------------
[res_holds, sup_holds, brekout_res, brekout_sup] = calcSupportResistance(close)

// ---------------------------------------------------------------------------------------------------------------------
// 🔥 STATE TRACKING
// ---------------------------------------------------------------------------------------------------------------------
var bool res_is_sup = na
var bool sup_is_res = na

switch
    brekout_res => res_is_sup := true
    res_holds   => res_is_sup := false

switch
    brekout_sup => sup_is_res := true
    sup_holds   => sup_is_res := false

// ---------------------------------------------------------------------------------------------------------------------
// 🔥 ALERTS
// ---------------------------------------------------------------------------------------------------------------------
strike_pe = int(getStrike(high[1], false))
ltp_pe    = getPELTP(strike_pe)
sym_pe    = getPESymbol(strike_pe)

strike_ce = int(getStrike(low[1], true))
ltp_ce    = getCELTP(strike_ce)
sym_ce    = getCESymbol(strike_ce)

msg1 = '{"message":"Res_Hold Price=' + str.tostring(high[1]) + ' Type=buyPE Strike=' + str.tostring(strike_pe) + ' StrikeLivePrice=' + str.tostring(ltp_pe) + ' Symbol=' + str.tostring(sym_pe) + ' Flag=true Time=' + formatTime(time[1]) + '"}'

msg2 = '{"message":"Sup_Hold Price=' + str.tostring(low[1]) + ' Type=buyCE Strike=' + str.tostring(strike_ce) + ' StrikeLivePrice=' + str.tostring(ltp_ce) + ' Symbol=' + str.tostring(sym_ce) + ' Flag=true Time=' + formatTime(time[1]) + '"}'

msg3 = '{"message":"Res_to_Sup Price=' + str.tostring(low[1]) + ' Type=buyCE Strike=' + str.tostring(strike_ce) + ' StrikeLivePrice=' + str.tostring(ltp_ce) + ' Symbol=' + str.tostring(sym_ce) + ' Flag=true Time=' + formatTime(time[1]) + '"}'

msg4 = '{"message":"Sup_to_Res Price=' + str.tostring(high[1]) + ' Type=buyPE Strike=' + str.tostring(strike_pe) + ' StrikeLivePrice=' + str.tostring(ltp_pe) + ' Symbol=' + str.tostring(sym_pe) + ' Flag=true Time=' + formatTime(time[1]) + '"}'
// ---------------------------------------------------------------------------------------------------------------------
// 🔥 EXECUTION (ONLY CHANGE APPLIED)
// ---------------------------------------------------------------------------------------------------------------------
offset = syminfo.mintick * 10

if res_holds and barstate.isconfirmed and not na(ltp_pe)
    label.new(bar_index[1], high[1] + offset, msg1, style=label.style_label_down, color=color.red, textcolor=color.white)
    alert(msg1, alert.freq_once_per_bar_close)

if sup_holds and barstate.isconfirmed and not na(ltp_ce)
    label.new(bar_index[1], low[1] - offset, msg2, style=label.style_label_up, color=color.green, textcolor=color.white)
    alert(msg2, alert.freq_once_per_bar_close)

if brekout_res and res_is_sup[1] and barstate.isconfirmed and not na(ltp_ce)
    label.new(bar_index[1], low[1], msg3, style=label.style_label_up, color=color.green, textcolor=color.white)
    alert(msg3, alert.freq_once_per_bar_close)

if brekout_sup and sup_is_res[1] and barstate.isconfirmed and not na(ltp_pe)
    label.new(bar_index[1], high[1], msg4, style=label.style_label_down, color=color.red, textcolor=color.white)
    alert(msg4, alert.freq_once_per_bar_close)



    '''

# ---------------------------------------------------------------------------------------------------------------------
# GENERATOR FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

MAX_SECURITIES = 40
SEC_PER_STRIKE = 2

def chunk_strikes(strikes, chunk_size):
    for i in range(0, len(strikes), chunk_size):
        yield strikes[i:i + chunk_size]

def generate_switch_block(strikes, prefix):
    lines = ["    switch strike"]
    for strike in strikes:
        lines.append(f"        {strike} => {prefix}_{strike}")
    lines.append("        => na")
    return "\n".join(lines)

def generate_pine_section(strikes, expiry):
    pe_symbols, ce_symbols = [], []
    ltp_pe, ltp_ce = [], []

    for strike in strikes:
        pe_symbols.append(f'pe_{strike} = "NSE:NIFTY{expiry}P{strike}"')
        ce_symbols.append(f'ce_{strike} = "NSE:NIFTY{expiry}C{strike}"')

    for strike in strikes:
        ltp_pe.append(f'ltp_pe_{strike} = request.security(pe_{strike}, timeframe.period, close)')
        ltp_ce.append(f'ltp_ce_{strike} = request.security(ce_{strike}, timeframe.period, close)')

    content = []
    content.append("// 🔥 PREDEFINED SYMBOLS")
    content.extend(pe_symbols)
    content.extend(ce_symbols)

    content.append("\n// 🔥 FETCH LTP")
    content.extend(ltp_pe)
    content.extend(ltp_ce)

    content.append("\n// 🔥 MAPPING FUNCTIONS")
    content.append("getPELTP(strike) =>")
    content.append(generate_switch_block(strikes, "ltp_pe"))

    content.append("\ngetCELTP(strike) =>")
    content.append(generate_switch_block(strikes, "ltp_ce"))

    content.append("\ngetPESymbol(strike) =>")
    content.append(generate_switch_block(strikes, "pe"))

    content.append("\ngetCESymbol(strike) =>")
    content.append(generate_switch_block(strikes, "ce"))

    return "\n".join(content)

def generate_multiple_scripts(start=23000, end=25000, step=50, expiry="260505"):
    strikes = list(range(start, end + 1, step))
    max_strikes = MAX_SECURITIES // SEC_PER_STRIKE

    chunks = list(chunk_strikes(strikes, max_strikes))

    for i, chunk in enumerate(chunks, 1):
        section = generate_pine_section(chunk, expiry)
        batch_name = f"Batch-{i}.1"

        full_script = (
            s.replace("{pine_content}", section)
            .replace("{batch_name}", batch_name)
        )

        filename = f"pine_script_part_{i}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_script)

        print(f"✅ Saved: {filename} | Strikes: {chunk[0]} → {chunk[-1]}")

# ---------------------------------------------------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------------------------------------------------
generate_multiple_scripts(23000, 25000, 50)