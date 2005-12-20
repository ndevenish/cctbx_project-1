# Primary PDB input processing.
# Based on:
#   http://www.rcsb.org/pdb/docs/format/pdbguide2.2/guide2.2_frame.html

import sys

connectivity_annotation_section = (
  "SSBOND",
  "LINK",
  "HYDBND",
  "SLTBRG",
  "CISPEP",
)

coordinate_section = (
  "MODEL",
  "ATOM",
  "SIGATM",
  "ANISOU",
  "SIGUIJ",
  "TER",
  "HETATM",
  "ENDMDL",
)

connectivity_section = (
  "CONECT",
)

class FormatError(RuntimeError): pass
class UnknownRecordName(FormatError): pass

class pdb_record(object):

  def __init__(self, raw_record,
        line_number=None,
        strict=False,
        ignore_columns_73_and_following=False):
    if (ignore_columns_73_and_following):
      self.raw = (raw_record.rstrip()[:72] + " "*80)[:80]
    else:
      self.raw = (raw_record.rstrip() + " "*80)[:80]
    self.line_number = line_number
    self.strict = strict
    self.record_name = (self.raw)[:6].upper().strip()
    if (self.record_name == "REMARK"):
      try:
        n = int(self.raw[7:10])
      except:
        self.record_name += "_UNKNOWN"
      else:
        self.record_name += "_%03d" % (n,)
    function_name = "read_" + self.record_name
    bound_function_object = getattr(self, function_name, None)
    if (bound_function_object is None):
      self.is_interpreted = False
    else:
      self.is_interpreted = True
      bound_function_object()

  def show(self, f=None):
    if (f is None): f = sys.stdout
    print >> f, "PDB %s record:" % self.record_name
    for key,value in self.__dict__.items():
      if (key == "record_name"): continue
      print >> f, "  %s:" % key, value

  def error_prefix(self):
    if (self.line_number is None):
      return "Error: "
    else:
      return "Error: Line: %d: " % self.line_number

  def raise_FormatError(self, message=None):
    if (message is None):
      message = "Corrupt " + self.record_name + " record."
    raise FormatError("%s%s" % (self.error_prefix(), message))

  def convert_number(self,
        str,
        target_type,
        error_message=None,
        substitute_value=0):
    try: return target_type(str)
    except ValueError:
      if (self.strict): self.raise_FormatError(message=error_message)
    return substitute_value

  def assert_is_interpreted(self):
    if (not (self.record_name.startswith("REMARK") or self.is_interpreted)):
      raise UnknownRecordName("%sRecord name %s not recognized." % (
        self.error_prefix(), self.record_name))

  def read_HEADER(self):
    # 11 - 50  String(40)    classification  Classifies the molecule(s)
    # 51 - 59  Date          depDate         Deposition date.  This is the date
    #                                        the coordinates were received by
    #                                        the PDB
    # 63 - 66  IDcode        idCode          This identifier is unique within
    #                                        PDB
    self.classification = self.raw[10:50]
    self.depDate = self.raw[50:59]
    self.idCode = self.raw[62:66]

  def read_MASTER(self):
    # 11 - 15  Integer        numRemark     Number of REMARK records
    # 16 - 20  Integer        "0"
    # 21 - 25  Integer        numHet        Number of HET records
    # 26 - 30  Integer        numHelix      Number of HELIX records
    # 31 - 35  Integer        numSheet      Number of SHEET records
    # 36 - 40  Integer        numTurn       Number of TURN records
    # 41 - 45  Integer        numSite       Number of SITE records
    # 46 - 50  Integer        numXform      Number of coordinate transformation
    # 51 - 55  Integer        numCoord      Number of atomic coordinate records
    # 56 - 60  Integer        numTer        Number of TER records
    # 61 - 65  Integer        numConect     Number of CONECT records
    # 66 - 70  Integer        numSeq        Number of SEQRES records
    self.numRemark = self.convert_number(self.raw[10:15], int)
    self.numHet = self.convert_number(self.raw[20:25], int)
    self.numHelix = self.convert_number(self.raw[25:30], int)
    self.numSheet = self.convert_number(self.raw[30:35], int)
    self.numTurn = self.convert_number(self.raw[35:40], int)
    self.numSite = self.convert_number(self.raw[40:45], int)
    self.numXform = self.convert_number(self.raw[45:50], int)
    self.numCoord = self.convert_number(self.raw[50:55], int)
    self.numTer = self.convert_number(self.raw[55:60], int)
    self.numConect = self.convert_number(self.raw[60:65], int)
    self.numSeq = self.convert_number(self.raw[65:70], int)

  def read_EXPDTA(self):
    #  9 - 10  Continuation   continuation  Allows concatenation of
    #                                       multiple records.
    # 11 - 70  List           technique     The experimental technique(s)
    #                                       with optional comment
    #                                       describing the sample
    #                                       or experiment.
    self.continuation = self.raw[8:10]
    self.technique = self.raw[10:70]
    TECH = self.technique.upper()
    self.keywords = []
    for keyword in ("ELECTRON DIFFRACTION",
                    "FIBER DIFFRACTION",
                    "FLUORESCENCE TRANSFER",
                    "NEUTRON DIFFRACTION",
                    "NMR",
                    "THEORETICAL MODEL",
                    "X-RAY DIFFRACTION"):
      if (TECH.find(keyword) >= 0):
        self.keywords.append(keyword)

  def read_REMARK_002(self):
    self.text = self.raw[11:70]
    flds = self.raw[11:38].split()
    if (    len(flds) == 3
        and flds[0].upper() == "RESOLUTION."
        and flds[2].upper() == "ANGSTROMS."):
      try: resolution = float(flds[1])
      except: pass
      else: self.resolution = resolution

  def read_CRYST1(self):
    #  7 - 15       Real(9.3)      a             a (Angstroms).
    # 16 - 24       Real(9.3)      b             b (Angstroms).
    # 25 - 33       Real(9.3)      c             c (Angstroms).
    # 34 - 40       Real(7.2)      alpha         alpha (degrees).
    # 41 - 47       Real(7.2)      beta          beta (degrees).
    # 48 - 54       Real(7.2)      gamma         gamma (degrees).
    # 56 - 66       LString        sGroup        Space group.
    # 67 - 70       Integer        z             Z value.
    self.ucparams = [self.raw[ 6:15], self.raw[15:24], self.raw[24:33],
                     self.raw[33:40], self.raw[40:47], self.raw[47:54]]
    self.sGroup = self.raw[55:66].strip()
    self.z = self.raw[66:70]
    if (len(" ".join(self.ucparams).strip()) == 0):
      self.ucparams = None
    else:
      try: self.ucparams = [float(u) for u in self.ucparams]
      except ValueError:
        self.raise_FormatError("Corrupt unit cell parameters.")
    if (not self.sGroup): self.sGroup = None
    if (self.z.strip()):
      try: self.z = int(self.z)
      except ValueError: self.raise_FormatError("Corrupt Z value.")
    else: self.z = None

  def read_SCALEn(self):
    #  1 -  6       Record name    "SCALEn"       n=1, 2, or 3
    # 11 - 20       Real(10.6)     s[n][1]        Sn1
    # 21 - 30       Real(10.6)     s[n][2]        Sn2
    # 31 - 40       Real(10.6)     s[n][3]        Sn3
    # 46 - 55       Real(10.5)     u[n]           Un
    self.n = int(self.record_name[5])
    values = []
    for i in [10,20,30,45]:
      fld = self.raw[i:i+10]
      if (len(fld.strip()) == 0):
        value = 0
      else:
        try: value = float(fld)
        except ValueError: raise self.raise_FormatError()
      values.append(value)
    self.Sn1, self.Sn2, self.Sn3, self.Un = values

  def read_SCALE1(self):
    self.read_SCALEn()

  def read_SCALE2(self):
    self.read_SCALEn()

  def read_SCALE3(self):
    self.read_SCALEn()

  def read_ATOM_01_27(self):
    #  7 - 11  Integer       serial        Atom serial number.
    # 13 - 16  Atom          name          Atom name.
    # 17       Character     altLoc        Alternate location indicator.
    # 18 - 20  Residue name  resName       Residue name.
    # 22       Character     chainID       Chain identifier.
    # 23 - 26  Integer       resSeq        Residue sequence number.
    # 27       AChar         iCode         Code for insertion of residues.
    try: self.serial = int(self.raw[6:11])
    except ValueError:
      if (self.strict):
        self.raise_FormatError("Atom serial number must be an integer.")
      else:
        self.serial = 0
    self.name = self.raw[12:16]
    self.altLoc = self.raw[16]
    self.resName = self.raw[17:20]
    self.column_21 = self.raw[20]
    self.chainID = self.raw[21]
    try: self.resSeq = int(self.raw[22:26])
    except ValueError:
      if (self.strict):
        self.raise_FormatError("Residue sequence number must be an integer.")
      else:
        self.resSeq = 0
    self.iCode = self.raw[26]

  def read_ATOM(self):
    self.read_ATOM_01_27()
    # 31 - 38  Real(8.3)     x             Orthogonal coordinates for X in
    #                                      Angstroms.
    # 39 - 46  Real(8.3)     y             Orthogonal coordinates for Y in
    #                                      Angstroms.
    # 47 - 54  Real(8.3)     z             Orthogonal coordinates for Z in
    #                                      Angstroms.
    # 55 - 60  Real(6.2)     occupancy     Occupancy.
    # 61 - 66  Real(6.2)     tempFactor    Temperature factor.
    try:
      self.coordinates = [float(x) for x in (self.raw[30:38],
                                             self.raw[38:46],
                                             self.raw[46:54])]
    except ValueError:
      self.raise_FormatError("Coordinates must be floating point numbers.")
    if (self.raw[54:60] == " "*6):
      self.occupancy = 1.
    else:
      try: self.occupancy = float(self.raw[54:60])
      except ValueError: self.raise_FormatError(
        "Occupancy must be a floating point number.")
    if (self.raw[60:66] == " "*6):
      self.tempFactor = 0.
    else:
      try: self.tempFactor = float(self.raw[60:66])
      except ValueError: self.raise_FormatError(
        "Temperature factor must be a floating point number.")
    self.read_ATOM_73_80()

  def read_ATOM_73_80(self):
    # 73 - 76  LString(4)    segID         Segment identifier, left-justified.
    # 77 - 78  LString(2)    element       Element symbol, right-justified.
    # 79 - 80  LString(2)    charge        Charge on the atom.
    self.segID = self.raw[72:76]
    self.element = self.raw[76:78]
    self.charge = self.raw[78:80]

  def read_HETATM(self):
    self.read_ATOM()

  def read_SIGATM(self):
    self.read_ATOM()
    self.sigCoor = self.coordinates
    self.sigOcc = self.occupancy
    self.sigTemp = self.tempFactor
    del self.coordinates, self.occupancy, self.tempFactor

  def read_ANISOU(self):
    self.read_ATOM_01_27()
    # 29 - 35  Integer       u[0][0]     U(1,1)
    # 36 - 42  Integer       u[1][1]     U(2,2)
    # 43 - 49  Integer       u[2][2]     U(3,3)
    # 50 - 56  Integer       u[0][1]     U(1,2)
    # 57 - 63  Integer       u[0][2]     U(1,3)
    # 64 - 70  Integer       u[1][2]     U(2,3)
    try:
      uij = [int(x) for x in (self.raw[28:35],
                              self.raw[35:42],
                              self.raw[42:49],
                              self.raw[49:56],
                              self.raw[56:63],
                              self.raw[63:70])]
    except ValueError:
      self.raise_FormatError("u[i][j] must be integer numbers.")
    self.Ucart = [u / 10000. for u in uij]
    self.read_ATOM_73_80()

  def read_SIGUIJ(self):
    self.read_ANISOU()
    self.sigUcart = self.Ucart
    del self.Ucart

  def read_TER(self):
    #  7 - 11  Integer         serial     Serial number.
    # 18 - 20  Residue name    resName    Residue name.
    # 22       Character       chainID    Chain identifier.
    # 23 - 26  Integer         resSeq     Residue sequence number.
    # 27       AChar           iCode      Insertion code.
    self.serial = self.convert_number(self.raw[6:11], int,
      error_message="Serial number must be an integer.")
    self.resName = self.raw[17:20]
    self.chainID = self.raw[21]
    self.resSeq = self.convert_number(self.raw[22:26], int,
      error_message="Residue sequence number must be an integer.")
    self.iCode = self.raw[26]

  def read_MODEL(self):
    # 11 - 14  Integer        serial        Model serial number.
    if (self.strict):
      fld = self.raw[10:14]
    else:
      fld = self.raw[6:]
    self.serial = self.convert_number(fld, int,
      error_message="Model serial number must be an integer.")

  def read_ENDMDL(self):
    pass

  def read_CONECT(self):
    #  7 - 11  Integer   serial          Atom serial number
    # 12 - 16  Integer   serial          Serial number of bonded atom
    # 17 - 21  Integer   serial          Serial number of bonded atom
    # 22 - 26  Integer   serial          Serial number of bonded atom
    # 27 - 31  Integer   serial          Serial number of bonded atom
    # 32 - 36  Integer   serial          Serial number of hydrogen bonded atom
    # 37 - 41  Integer   serial          Serial number of hydrogen bonded atom
    # 42 - 46  Integer   serial          Serial number of salt bridged atom
    # 47 - 51  Integer   serial          Serial number of hydrogen bonded atom
    # 52 - 56  Integer   serial          Serial number of hydrogen bonded atom
    # 57 - 61  Integer   serial          Serial number of salt bridged atom
    self.serial = self.convert_number(self.raw[6:11], int,
      "Serial number must be an integer.")
    sn = []
    for i in xrange(11,61,5):
      fld = self.raw[i:i+5]
      if (len(fld.strip()) == 0):
        sn.append(None)
      else:
        try: sn.append(int(fld))
        except ValueError:
          if (self.strict):
            self.raise_FormatError(
              "Serial number of bonded atom must be an integer.")
          sn.append(None)
    assert len(sn) == 10
    self.serial_numbers_bonded_atoms = sn[:4]
    self.serial_numbers_hydrogen_bonded_atoms = sn[4:6] + sn[7:9]
    self.serial_numbers_salt_bridged_atoms = [sn[6], sn[9]]

  def read_LINK(self):
    # 13 - 16      Atom            name1       Atom name.
    # 17           Character       altLoc1     Alternate location indicator.
    # 18 - 20      Residue name    resName1    Residue name.
    # 22           Character       chainID1    Chain identifier.
    # 23 - 26      Integer         resSeq1     Residue sequence number.
    # 27           AChar           iCode1      Insertion code.
    # 31 - 40      distance (REFMAC extension: F10.5)
    # 43 - 46      Atom            name2       Atom name.
    # 47           Character       altLoc2     Alternate location indicator.
    # 48 - 50      Residue name    resName2    Residue name.
    # 52           Character       chainID2    Chain identifier.
    # 53 - 56      Integer         resSeq2     Residue sequence number.
    # 57           AChar           iCode2      Insertion code.
    # 60 - 65      SymOP           sym1        Symmetry operator for 1st atom.
    # 67 - 72      SymOP           sym2        Symmetry operator for 2nd atom.
    # 73 - 80      margin (REFMAC extension: _chem_link.id)
    self.name1 = self.raw[12:16]
    self.altLoc1 = self.raw[16]
    self.resName1 = self.raw[17:20]
    self.chainID1 = self.raw[21]
    self.resSeq1 = self.convert_number(self.raw[22:26], int,
      "Serial number be an integer.")
    self.iCode1 = self.raw[26]
    try: self.distance = float(self.raw[30:40])
    except ValueError: self.distance = None
    self.name2 = self.raw[42:46]
    self.altLoc2 = self.raw[46]
    self.resName2 = self.raw[47:50]
    self.chainID2 = self.raw[51]
    self.resSeq2 = self.convert_number(self.raw[52:56], int,
      "Serial number be an integer.")
    self.iCode2 = self.raw[56]
    self.sym1 = self.raw[59:65]
    self.sym2 = self.raw[66:72]
    self.margin = self.raw[72:80]

  def read_SLTBRG(self):
    self.read_LINK()

  def read_SSBOND(self):
    #  8 - 10    Integer         serNum      Serial number.
    # 12 - 14    LString(3)      "CYS"       Residue name.
    # 16         Character       chainID1    Chain identifier.
    # 18 - 21    Integer         seqNum1     Residue sequence number.
    # 22         AChar           icode1      Insertion code.
    # 26 - 28    LString(3)      "CYS"       Residue name.
    # 30         Character       chainID2    Chain identifier.
    # 32 - 35    Integer         seqNum2     Residue sequence number.
    # 36         AChar           icode2      Insertion code.
    # 60 - 65    SymOP           sym1        Symmetry operator for 1st residue.
    # 67 - 72    SymOP           sym2        Symmetry operator for 2nd residue.
    # 73 - 80    margin (REFMAC extension: _chem_link.id)
    self.serNum = self.convert_number(self.raw[7:10], int,
      "Serial number be an integer.")
    self.resName1 = self.raw[11:14]
    self.chainID1 = self.raw[15]
    self.resSeq1 = self.convert_number(self.raw[17:21], int,
      "Serial number be an integer.")
    self.iCode1 = self.raw[21]
    self.resName2 = self.raw[25:28]
    self.chainID2 = self.raw[29]
    self.resSeq2 = self.convert_number(self.raw[31:35], int,
      "Serial number be an integer.")
    self.iCode2 = self.raw[35]
    self.sym1 = self.raw[59:65]
    self.sym2 = self.raw[66:72]
    self.margin = self.raw[72:80]

class columns_73_76_evaluator(object):

  def __init__(self, raw_records,
        is_frequent_threshold_atom_records=1000,
        is_frequent_threshold_other_records=100):
    self.raw_records = list(raw_records)
    atom_columns_73_76_dict = {}
    other_columns_73_76_dict = {}
    for raw_record in self.raw_records:
      if (raw_record[:6] in ("ATOM  ", "HETATM")):
        columns_73_76_dict = atom_columns_73_76_dict
      else:
        columns_73_76_dict = other_columns_73_76_dict
      if (    raw_record[:6] not in ("SIGATM", "ANISOU", "SIGUIJ", "TER   ")
          and len(raw_record.rstrip()) >= 80):
        field = raw_record[72:76]
        if (field != "    "):
          try: columns_73_76_dict[field] += 1
          except KeyError: columns_73_76_dict[field] = 1
    if (len(atom_columns_73_76_dict) == 0):
      self.finding = "Blank columns 73-76 on ATOM and HETATM records."
      self.is_old_style = False
      return
    if (    len(other_columns_73_76_dict) == 1
        and len(atom_columns_73_76_dict) == 1
        and len(other_columns_73_76_dict.keys()[0].strip()) == 4
        and other_columns_73_76_dict.keys() == atom_columns_73_76_dict.keys()):
      self.finding = "Exactly one common label in columns 73-76."
      self.is_old_style = True
      return
    common_four_character_field = None
    sum_counts_common_four_character_field = 0
    for field in atom_columns_73_76_dict.keys():
      if (len(field.strip()) != 4): continue
      if (field in other_columns_73_76_dict):
        if (    atom_columns_73_76_dict[field]
                > is_frequent_threshold_atom_records
            and other_columns_73_76_dict[field]
                > is_frequent_threshold_other_records):
          self.finding = "Frequent common labels in columns 73-76."
          self.is_old_style = True
          return
        sum_counts = atom_columns_73_76_dict[field] \
                   + other_columns_73_76_dict[field]
        if (sum_counts_common_four_character_field < sum_counts):
          common_four_character_field = field
          sum_counts_common_four_character_field = sum_counts
    if (sum_counts_common_four_character_field == 0):
      self.finding =  "No common label in columns 73-76."
      self.is_old_style = False
      return
    three_char_dicts = []
    for columns_73_76_dict in [atom_columns_73_76_dict,
                               other_columns_73_76_dict]:
      three_char_dict = {}
      for field,n in columns_73_76_dict.items():
        field = field[:3]
        try: three_char_dict[field] += n
        except KeyError: three_char_dict[field] = n
      three_char_dicts.append(three_char_dict)
    if (    len(three_char_dicts[0]) == 1
        and len(three_char_dicts[1]) == 1
        and len(three_char_dicts[0].keys()[0].strip()) == 3
        and three_char_dicts[0].keys() == three_char_dicts[1].keys()):
      self.finding = "Exactly one common label in columns 73-76" \
                   + " comparing only the first three characters."
      self.is_old_style = True
      return
    self.finding = "Undecided."
    self.is_old_style = False

def collect_records(raw_records,
                    ignore_unknown=True,
                    ignore_coordinate_section=False,
                    ignore_master=False,
                    evaluate_columns_73_76=True):
  ignore_columns_73_and_following = False
  if (evaluate_columns_73_76):
    evaluation = columns_73_76_evaluator(
      raw_records=raw_records)
    raw_records = evaluation.raw_records
    ignore_columns_73_and_following = evaluation.is_old_style
  records = []
  line_number = 0
  for raw_record in raw_records:
    line_number += 1
    if (ignore_master and raw_record.startswith("MASTER")):
      continue
    r = pdb_record(
      raw_record=raw_record,
      line_number=line_number,
      ignore_columns_73_and_following=ignore_columns_73_and_following)
    if (ignore_unknown and not r.is_interpreted):
      continue
    if (ignore_coordinate_section and r.record_name in coordinate_section):
      continue
    records.append(r)
  return records
