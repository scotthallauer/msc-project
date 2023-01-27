import sys

def index_to_code(index: int):
  if index < 10:
    return "0" + str(index)
  else:
    return str(index)

if __name__ == "__main__":

  GENERATE_PREFIX = sys.argv[1]
  START_INDEX = int(sys.argv[2])
  STOP_INDEX = int(sys.argv[3])
  REFERENCE_INDEX = 1
  REFERENCE_FOLDER = "jobs/" + GENERATE_PREFIX.split("-")[0] + "/"

  for i in range(START_INDEX, STOP_INDEX + 1):
    REFERENCE_FILE = REFERENCE_FOLDER + GENERATE_PREFIX + "-" + index_to_code(REFERENCE_INDEX) + ".job"
    GENERATE_FILE = REFERENCE_FOLDER + GENERATE_PREFIX + "-" + index_to_code(i) + ".job"
    with open(REFERENCE_FILE, "r") as file:
      data = file.read()
      data = data.replace(GENERATE_PREFIX + "-" + index_to_code(REFERENCE_INDEX), GENERATE_PREFIX + "-" + index_to_code(i))
    with open(GENERATE_FILE, "w") as file:
      file.write(data)
  
  print("Files generated.")
