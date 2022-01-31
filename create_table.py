def find_entry_containing(list, string): # returns (first) index of item in list containing string, else -1
  for entry in range(len(list)):
    if string in list[entry]: return entry
  return -1

def transpose_2dlist(list): # [i][j] -> [j][i], assumes rectangular list
  result=[[None for i in range(len(list))] for j in range(len(list[0]))]
  for i in range(len(list)):
    for j in range(len(list[i])):
      result[j][i]=list[i][j]
  return result

def row_col(list, entry): # returns (row,col) of entry in (rectangular) 2d list, or (-1,-1) if cannot find entry. Works best if list has unique entries
  for row in range(len(list)):
    for col in range(len(list[0])):
      if entry==list[row][col]: return (row,col)
  return (-1,-1)

def csv_to_2dlist(csv, row_start): # converts spreadsheet (a .csv file) to more convenient 2D list, beginning at row row_start; skips empty lines
  sheet=open(csv,"r")
  lines=sheet.readlines()
  entries=[]
  for line in lines[row_start:]:
    nonempty=False
    row=line.split(",")
    for entry in row:
      if not (len(entry)==0 or entry.isspace()):
        nonempty=True
        break
    if nonempty: entries.append(row)
  return entries

def write_comma_delimited_line(filename, line): # line should be a list of strings; will write to end of file
  f=open(filename,"a+")
  for entry in line:
    if not entry.isspace(): f.write(entry+",")
  f.write("\n")
  f.close()

def LVR_output_con_and_pin_to_channel(output_con, src_pin): # output_con should be "J12" or "J13", src_pin should be '2','4','6','8'; converts to LVR channel #
  if not ((output_con in ["J12","J13"]) and (src_pin in ["2","4","6","8"])):
    print("Invalid LVR power specs")
    return "-1"
  else:
    ch=5-int(src_pin)/2
    if output_con=="J13": ch+=4.0
    return str(int(ch))

def surface_sense_label(posBP,fourASICdcbPower,tBB_con,output):
  # no need to safety check that output is acceptable value
  if tBB_con=="slave": return "slave"

  voltage="12"
  suffix="x" # these are bad labels for surface cables; sense cables used both for straight and stereo staves
  number=0
  if output=="dcb":
    voltage=fourASICdcbPower[0]+fourASICdcbPower[2]
    suffix=""
    number=str(int(tBB_con[1:])-8)
    if voltage=="25": number=str(int(number)-3)
  elif output=="hybrid_stereo":
    number=str(int(tBB_con[1:])-13)
  else: # hybrid_straight
    number=tBB_con[1:]

  return posBP+"_"+voltage+"_sense_"+number+suffix

def bp_con_JP_to_alt(JP, mirror): # converts JP # to alternative BP connector notation
  index=int(JP[2:])
  if mirror:
    if (index//2)%2==0: index+=2
    else: index-=2
  alt_labels=["X0M","X0S","S0S","S0M","X1M","X1S","S1S","S1M","X2M","X2S","S2S","S2M"]
  return alt_labels[index]

def bp_con_alt_to_JP(alt, mirror): # converts alternative BP connector notation to JP #
  # take advantage of mapping being 1-to-1
  for JP in range(12):
    if bp_con_JP_to_alt("JP"+str(JP), mirror)==alt: return "JP"+str(JP)
  return None # should never return

def reorganize_2dlist(key_phrase, entries): # give entries input as a 2D list, excluding headers; organize based on key_phrase
  return entries

def create_table(zPEPI, yPEPI, posBP):
  # inputs assume working on C-side: C-bot-IP-true, C-top-IP-mir, C-bot-mag-mir, C-top-mag-true are PEPIs
  # posBP is alpha/beta/gamma
  if not ((zPEPI in ["IP","mag"]) and (yPEPI in ["top","bot"]) and (posBP in ["alpha","beta","gamma"])):
    print("Provide valid PEPI specs")
    return

  out_file="output_csv_tables/surface_LVpower_tests_C_"+zPEPI+"_"+yPEPI+"_"+posBP+".csv"
  out_f=open(out_file,"w+")
  out_f.write("") # clear file, if it exists
  out_f.close()
  write_comma_delimited_line(out_file, ["BP Connector", "iBB/P2B2 Connector", "4ASIC-group (hybrid)/DCB power", "PPP Positronic",
                                        "Positronic Src", "Positronic Ret", "Surface LVR ID", "Surface LVR ch.", "Telemetry BB Connector",
                                        "PPP RJ45 Coupler", "Surface Sense Label"]) # make table header

  mirror=False
  if (zPEPI=="mag" and yPEPI=="bot") or (zPEPI=="IP" and yPEPI=="top"): mirror=True

  # For the surface, I'll primarily use Scott's PPPtoLVR_Mapping_FinalSurface.xlxs file from EDMS as a reference. I break this up into smaller
  # reference files for easier access, but all the info is the same. Note that this file is only for mag side; for IP, you'll need to reference
  # some document that gives info about what depopulates on IP (IP is just a subset of mag; everything is the same except depop).
  # I will try to organize the output tables according to BP connector, since this will be useful for testing the hybrids; for the DCBs, this
  # isn't really optimal, but one could always reorganize the tables. (TODO: add reorganizing function, since annoying in Excel)
  # To begin, I'll loop over the "PPP Name" for the given PEPI and BP position; I'll join straight hybrid + stereo hybrid + DCB together in one table.
  # Given a "PPP Name" the BP connector, iBB/P2B2 connector, and 4-ASIC group/DCB power (1.5V or 2.5V) are specified. From adjacent columns in the
  # same sheet, PPP power info and LVR info can be obtained. Using the BP connector and 4-ASIC group/DCB power info, one can then find the telemetryBB
  # connector (and thus also surface long sense line label) using Scott's testing table. From the telemetryBB connector, the PPP sense info can then
  # be obtained using the sense cabling sheets
  entries=[] # will be a 2D list; add headers as a final step
  scott_test_ref=csv_to_2dlist("ref/TelemetryWireMap_UTSurface_CSide.csv", 0)
  scott_test_ref_T=transpose_2dlist(scott_test_ref)
  scott_test_ref_straight=transpose_2dlist(scott_test_ref_T[:7])
  scott_test_ref_dcb=transpose_2dlist(scott_test_ref_T[8:15])
  scott_test_ref_stereo=transpose_2dlist(scott_test_ref_T[16:23])
  sensePPP_ref=csv_to_2dlist("ref/surface_sense_tBB_to_PPP_"+zPEPI+"_"+yPEPI+".csv", 0)
  offset=0
  if posBP=="beta": offset=10
  if posBP=="alpha": offset=20
  sensePPP_ref=transpose_2dlist(transpose_2dlist(sensePPP_ref)[offset:offset+9])[2:]
  for output in ["hybrid_stereo", "hybrid_straight", "dcb"]:
    ref_with_headers=csv_to_2dlist("ref/surface_power_"+output+"_"+zPEPI+"_"+yPEPI+"_"+posBP+".csv", 0)
    ref=csv_to_2dlist("ref/surface_power_"+output+"_"+zPEPI+"_"+yPEPI+"_"+posBP+".csv", 2)
    ref_T=transpose_2dlist(ref)
    for name in ref_T[1]:
      if "GND" in name: continue # dcb sheets have separate GND lines separate, but better to treat source/return together
      row=row_col(ref,name)[0]
      # the 2.5V entries complicate things a bit, so change their notation
      if "2V5" in name: name=name.replace("_","-",1)
      name_parts=name.split("_")
      bp_con=name_parts[0]
      bp_con_alt=None
      if output!="dcb": bp_con_alt=bp_con_JP_to_alt(bp_con, mirror)
      iBBP2B2_con=name_parts[1]
      fourASICdcbPower=name_parts[2]
      PPP_info=ref[row][2].replace(" ","").split("-")
      PPP_positronic=PPP_info[0]
      PPP_srcPin=PPP_info[1][0]
      PPP_retPin=str(int(PPP_srcPin)+8)
      surface_LVR_col=find_entry_containing(ref_with_headers[0], "LVR Surface")
      surface_LVR=ref[row][surface_LVR_col].replace(" ","").split("-")
      surface_LVR_ID=surface_LVR[0]
      surface_LVR_ch=LVR_output_con_and_pin_to_channel(surface_LVR[1], surface_LVR[2][0])
      ref_tBB=None
      if output=="hybrid_stereo": ref_tBB=scott_test_ref_stereo
      if output=="hybrid_straight": ref_tBB=scott_test_ref_straight
      if output=="dcb": ref_tBB=scott_test_ref_dcb
      # don't need to do a safety check for ref_tBB, since hard-coded
      # Note: when looking up telemetryBB connector, if cannot find the corresponding line in Scott's testing table, it's because the line is a slave
      tBB_con="slave"
      # unfortunately, need to be a little tricky for mirror cases (for hybrids only), since Scott only did table for a true PEPI
      bp_con_ref=bp_con
      tBB_row=-1
      if mirror and output!="dcb": bp_con_ref=bp_con_alt_to_JP(bp_con_alt, not mirror)
      if output!="dcb": tBB_row=find_entry_containing(transpose_2dlist(ref_tBB)[3], bp_con_ref+" "+fourASICdcbPower)
      # actually, for 2.5V, the entries are a little unique, so handle them separately
      if output=="dcb":
        if fourASICdcbPower!="2V5": tBB_row=find_entry_containing(transpose_2dlist(ref_tBB)[3], bp_con+" "+fourASICdcbPower)
        else: tBB_row=find_entry_containing(transpose_2dlist(ref_tBB)[3], bp_con.replace("-","_")+" "+fourASICdcbPower)
      if tBB_row!=-1: tBB_con=ref_tBB[tBB_row][0]
      surface_sense=surface_sense_label(posBP,fourASICdcbPower,tBB_con,output)
      PPP_sense="slave"
      if tBB_con!="slave": PPP_sense=sensePPP_ref[row_col(sensePPP_ref,tBB_con)[0]][0]
      if tBB_con!="slave" and mirror: # emphasize that you are uncertain about how this is being handled
        tBB_con+="??"
        surface_sense+="??"
        PPP_sense+="??"
      print([bp_con, iBBP2B2_con, fourASICdcbPower, PPP_positronic, PPP_srcPin, PPP_retPin, surface_LVR_ID, surface_LVR_ch, tBB_con, PPP_sense, surface_sense])
      write_comma_delimited_line(out_file, [bp_con, iBBP2B2_con, fourASICdcbPower, PPP_positronic, PPP_srcPin, PPP_retPin, surface_LVR_ID, surface_LVR_ch, tBB_con, PPP_sense, surface_sense])



create_table("mag","bot","alpha")
