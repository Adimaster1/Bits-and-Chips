read_liberty osu018_stdcells.lib
read_verilog synth_netlist.v
link_design heavy_calculator

create_clock -name clk -period 2.0 [get_ports clk]

# Dynamically apply delay to all input ports except clk
foreach port [all_inputs] {
    set port_name [get_name $port]
    if {$port_name ne "clk"} {
        set_input_delay -clock clk 0.0 $port
    }
}

set_output_delay -clock clk 0.0 [all_outputs]

report_checks -digits 3
exit
