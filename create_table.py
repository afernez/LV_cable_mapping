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

def write_comma_delimited_line(filename, line): # line should be a list of strings; will write to end of file
  f=open(filename,"a+")
  for entry in line:
    if not entry.isspace(): f.write(entry+",")
  f.write("\n")
  f.close()

def create_table(zPEPI, yPEPI, posBP):
  # inputs assume working on C-side: C-bot-IP-true, C-top-IP-mir, C-bot-mag-mir, C-top-mag-true are PEPIs
  # posBP is alpha/beta/gamma
  if not ((zPEPI=="IP" or zPEPI=="mag") and (yPEPI=="top" or yPEPI=="bot") and (posBP=="alpha" or posBP=="beta" or posBP=="gamma")):
    print("Provide valid PEPI specs")
    return

  # For the surface, I'll primarily use Scott's PPPtoLVR_Mapping_FinalSurface.xlxs file from EDMS as a reference. I break this up into smaller
  # reference files for easier access, but all the info is the same. Note that this file is only for mag side; for IP, you'll need to reference
  # some document that gives info about what depopulates on IP (IP is just a subset of mag; everything is the same except depop).
  # I will try to organize the output tables according to BP connector, since this will be useful for testing the hybrids; for the DCBs, this
  # isn't really optimal, but one could always reorganize the tables. (TODO: add reorganizing function, since annoying in Excel)
  # To begin, I'll loop over the "PPP Name" for the given PEPI and BP position; I'll join straight hybrid + stereo hybrid + DCB together in one table.
  # Given a "PPP Name" the BP connector, iBB/P2B2 connector, and 4-ASIC group/DCB power (1.5V or 2.5V) are specified. From adjacent columns in the
  # same sheet, PPP power info and LVR info can be obtained. Using the BP connector and 4-ASIC group/DCB power info, one can then find the telemetryBB
  # connector (and thus also surface long sense line label) using Scott's testing table. From the telemetryBB connector, the PPP sense info can then
  # be obtained using the sense cabling sheets.
  # TODO loop making tables ...
  # Note: when looking up telemetryBB connector, if cannot the corresponding line in Scott's testing table, it's because the line is a slave
