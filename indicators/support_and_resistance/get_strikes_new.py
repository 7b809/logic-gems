import os
import math


# -------------------------------------------------------------------------------------------------
# FULL PINE TEMPLATE
# -------------------------------------------------------------------------------------------------

PINE_TEMPLATE = """
//@version=5
indicator("SR Batch {batch_num}", shorttitle="SR B{batch_num}", overlay=true, max_boxes_count=50)

// ---------------------------------------------------------------------------------------------------------------------
// INPUTS
// ---------------------------------------------------------------------------------------------------------------------

lookbackPeriod = input.int(20, "Lookback Period")
vol_len = input.int(2, "Delta Volume Filter Length")
box_withd = input.float(1, "Adjust Box Width")

// ---------------------------------------------------------------------------------------------------------------------
// TEST MODE
// ---------------------------------------------------------------------------------------------------------------------

enableTestAlerts = input.bool(false, "Enable Test Alerts")
testAlertTickGap = input.int(10, "Test Alert Every N Bars")

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

    if isBuyVolume
        posVol += volume
    else
        negVol -= volume

    posVol + negVol


formatTime(_time) =>
    str.format_time(_time, "yyyy-MM-dd HH:mm", "Asia/Kolkata")


getStrike(price, isCE) =>
    step = 50.0
    isCE ? math.floor(price / step) * step : math.ceil(price / step) * step


{STATIC_BLOCK}


// ---------------------------------------------------------------------------------------------------------------------
// OPTION DATA BUILDER
// ---------------------------------------------------------------------------------------------------------------------

buildOptionData(_price, _isCE) =>
    strike = getStrike(_price, _isCE)
    symbol = _isCE ? getCESymbol(strike) : getPESymbol(strike)
    ltp = _isCE ? getCELTP(strike) : getPELTP(strike)
    [strike, symbol, ltp]


// ---------------------------------------------------------------------------------------------------------------------
// SUPPORT / RESISTANCE LOGIC
// ---------------------------------------------------------------------------------------------------------------------

calcSupportResistance(src, lookbackPeriod) =>

    Vol = upAndDownVolume()

    vol_hi = ta.highest(Vol / 2.5, vol_len)
    vol_lo = ta.lowest(Vol / 2.5, vol_len)

    var float supportLevel = na
    var float supportLevel_1 = na

    var float resistanceLevel = na
    var float resistanceLevel_1 = na

    var box sup = na
    var box res = na

    pivotHigh = ta.pivothigh(src, lookbackPeriod, lookbackPeriod)
    pivotLow = ta.pivotlow(src, lookbackPeriod, lookbackPeriod)

    atr = ta.atr(200)
    withd = atr * box_withd

    if (not na(pivotLow)) and Vol > vol_hi

        supportLevel := pivotLow
        supportLevel_1 := supportLevel - withd

        topLeft = chart.point.from_index(bar_index - lookbackPeriod, supportLevel)
        bottomRight = chart.point.from_index(bar_index, supportLevel_1)

        sup := box.new(top_left = topLeft, bottom_right = bottomRight, border_color = color.green, bgcolor = color.new(color.green, 85))

    if (not na(pivotHigh)) and Vol < vol_lo

        resistanceLevel := pivotHigh
        resistanceLevel_1 := resistanceLevel + withd

        topLeft = chart.point.from_index(bar_index - lookbackPeriod, resistanceLevel)
        bottomRight = chart.point.from_index(bar_index, resistanceLevel_1)

        res := box.new(top_left = topLeft, bottom_right = bottomRight, border_color = color.red, bgcolor = color.new(color.red, 85))

    sup.set_right(bar_index + 1)
    res.set_right(bar_index + 1)

    brekout_res = ta.crossover(low, resistanceLevel_1)
    res_holds = ta.crossunder(high, resistanceLevel)

    sup_holds = ta.crossover(low, supportLevel)
    brekout_sup = ta.crossunder(high, supportLevel_1)

    [supportLevel, resistanceLevel, brekout_res, res_holds, sup_holds, brekout_sup, Vol]


// ---------------------------------------------------------------------------------------------------------------------
// MAIN CALCULATION
// ---------------------------------------------------------------------------------------------------------------------

[supportLevel, resistanceLevel, brekout_res, res_holds, sup_holds, brekout_sup, Vol] = calcSupportResistance(close, lookbackPeriod)


// ---------------------------------------------------------------------------------------------------------------------
// STATE
// ---------------------------------------------------------------------------------------------------------------------

var bool res_is_sup = na
var bool sup_is_res = na

switch
    brekout_res => res_is_sup := true
    res_holds => res_is_sup := false

switch
    brekout_sup => sup_is_res := true
    sup_holds => sup_is_res := false


// ---------------------------------------------------------------------------------------------------------------------
// PLOTS
// ---------------------------------------------------------------------------------------------------------------------

plotchar(res_holds, "Resistance Holds", "◆", color=color.red, location=location.abovebar, offset=-1)

plotchar(sup_holds, "Support Holds", "◆", color=color.green, location=location.belowbar, offset=-1)


// ---------------------------------------------------------------------------------------------------------------------
// SUPPORT HOLD
// ---------------------------------------------------------------------------------------------------------------------

if sup_holds

    [strike, symbol, optionLtp] = buildOptionData(close, false)

    msg = "Sup_Hold Price=" + str.tostring(math.round(supportLevel, 2)) + " Type=buyPE Strike=" + str.tostring(strike) + " StrikeLivePrice=" + str.tostring(math.round(optionLtp, 2)) + " Symbol=" + symbol + " Flag=true Time=" + formatTime(time)

    label.new(bar_index, supportLevel, msg, style = label.style_label_up, color = color.green, textcolor = color.white)

    alert(msg, alert.freq_once_per_bar_close)


// ---------------------------------------------------------------------------------------------------------------------
// RESISTANCE HOLD
// ---------------------------------------------------------------------------------------------------------------------

if res_holds

    [strike, symbol, optionLtp] = buildOptionData(close, true)

    msg = "Res_Hold Price=" + str.tostring(math.round(resistanceLevel, 2)) + " Type=buyPE Strike=" + str.tostring(strike) + " StrikeLivePrice=" + str.tostring(math.round(optionLtp, 2)) + " Symbol=" + symbol + " Flag=true Time=" + formatTime(time)

    label.new(bar_index, resistanceLevel, msg, style = label.style_label_down, color = color.red, textcolor = color.white)

    alert(msg, alert.freq_once_per_bar_close)


// ---------------------------------------------------------------------------------------------------------------------
// BREAK SUPPORT
// ---------------------------------------------------------------------------------------------------------------------

if brekout_sup and not sup_is_res[1]

    [strike, symbol, optionLtp] = buildOptionData(close, false)

    msg = "Break_Sup Price=" + str.tostring(math.round(supportLevel[1], 2)) + " Type=buyPE Strike=" + str.tostring(strike) + " StrikeLivePrice=" + str.tostring(math.round(optionLtp, 2)) + " Symbol=" + symbol + " Flag=true Time=" + formatTime(time)

    label.new(bar_index[1], supportLevel[1], msg, style = label.style_label_down, color = #7e1e1e, textcolor = color.white)

    alert(msg, alert.freq_once_per_bar_close)


// ---------------------------------------------------------------------------------------------------------------------
// BREAK RESISTANCE
// ---------------------------------------------------------------------------------------------------------------------

if brekout_res and not res_is_sup[1]

    [strike, symbol, optionLtp] = buildOptionData(close, true)

    msg = "Break_Res Price=" + str.tostring(math.round(resistanceLevel[1], 2)) + " Type=buyCE Strike=" + str.tostring(strike) + " StrikeLivePrice=" + str.tostring(math.round(optionLtp, 2)) + " Symbol=" + symbol + " Flag=true Time=" + formatTime(time)

    label.new(bar_index[1], resistanceLevel[1], msg, style = label.style_label_up, color = #2b6d2d, textcolor = color.white)

    alert(msg, alert.freq_once_per_bar_close)

// ---------------------------------------------------------------------------------------------------------------------
// TEST ALERTS
// ---------------------------------------------------------------------------------------------------------------------

if enableTestAlerts and (bar_index % testAlertTickGap == 0)

    testMsg = "TEST_ALERT Price=" + str.tostring(close) + " Type=buyCE Strike=24000 StrikeLivePrice=100 Symbol=NSE:NIFTY260512C24000 Flag=true Time=" + formatTime(time)

    label.new(bar_index, high, testMsg, style = label.style_label_down, color = color.orange, textcolor = color.white)

    alert(testMsg, alert.freq_once_per_bar)    
    
    """


# -------------------------------------------------------------------------------------------------
# STATIC BLOCK GENERATOR
# -------------------------------------------------------------------------------------------------

def generate_static_block(strikes, expiry):

    code = []

    code.append("// 🔥 PREDEFINED SYMBOLS")

    for strike in strikes:
        code.append(f'pe_{strike} = "NSE:NIFTY{expiry}P{strike}"')

    for strike in strikes:
        code.append(f'ce_{strike} = "NSE:NIFTY{expiry}C{strike}"')

    code.append("")
    code.append("// 🔥 FETCH LTP")

    for strike in strikes:
        code.append(f'ltp_pe_{strike} = request.security(pe_{strike}, timeframe.period, close)')

    for strike in strikes:
        code.append(f'ltp_ce_{strike} = request.security(ce_{strike}, timeframe.period, close)')

    # -------------------------------------------------------------------------------------------------

    code.append("")
    code.append("// 🔥 MAPPING FUNCTIONS")

    code.append("getPELTP(strike) =>")
    code.append("    switch strike")

    for strike in strikes:
        code.append(f'        {strike} => ltp_pe_{strike}')

    code.append("        => na")

    # -------------------------------------------------------------------------------------------------

    code.append("")
    code.append("getCELTP(strike) =>")
    code.append("    switch strike")

    for strike in strikes:
        code.append(f'        {strike} => ltp_ce_{strike}')

    code.append("        => na")

    # -------------------------------------------------------------------------------------------------

    code.append("")
    code.append("getPESymbol(strike) =>")
    code.append("    switch strike")

    for strike in strikes:
        code.append(f'        {strike} => pe_{strike}')

    code.append("        => na")

    # -------------------------------------------------------------------------------------------------

    code.append("")
    code.append("getCESymbol(strike) =>")
    code.append("    switch strike")

    for strike in strikes:
        code.append(f'        {strike} => ce_{strike}')

    code.append("        => na")

    return "\n".join(code)


# -------------------------------------------------------------------------------------------------
# MAIN GENERATOR
# -------------------------------------------------------------------------------------------------

def generate_multiple_scripts(
    start,
    end,
    step,
    expiry="260512",
    batch_size=30,
    output_folder="generated_pines"
):

    os.makedirs(output_folder, exist_ok=True)

    strikes = list(range(start, end + step, step))

    total_batches = math.ceil(len(strikes) / batch_size)

    print(f"Total Strikes : {len(strikes)}")
    print(f"Batch Size    : {batch_size}")
    print(f"Total Files   : {total_batches}")

    for batch_num in range(total_batches):

        start_idx = batch_num * batch_size
        end_idx = start_idx + batch_size

        batch_strikes = strikes[start_idx:end_idx]

        first_strike = batch_strikes[0]
        last_strike = batch_strikes[-1]

        print(f"Generating Batch {batch_num + 1} -> {first_strike} to {last_strike}")

        static_block = generate_static_block(batch_strikes, expiry)

        full_pine = PINE_TEMPLATE.replace(
            "{STATIC_BLOCK}",
            static_block
        ).replace(
            "{batch_num}",
            str(batch_num + 1)
        )

        filename = f"sr_batch_{batch_num + 1}_{first_strike}_{last_strike}_{expiry}.pine"

        filepath = os.path.join(output_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_pine)

        print(f"Saved: {filepath}")


# -------------------------------------------------------------------------------------------------
# EXAMPLE
# -------------------------------------------------------------------------------------------------

generate_multiple_scripts(
    start=23000,
    end=25000,
    step=50,
    expiry="260512",
    batch_size=20
)