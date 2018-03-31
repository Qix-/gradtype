import matplotlib
import sys

# Do not display GUI only when generating output
if __name__ != '__main__' or len(sys.argv) >= 3:
  matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sklearn.decomposition

# Internal
import dataset
import model as gradtype_model

COLOR_MAP = plt.cm.gist_rainbow

def to_color(index):
  return index / (len(dataset.LABELS) - 1)

def pca(train_coords, validate_coords, fname):
  fig = plt.figure(1, figsize=(8, 6))
  ax = Axes3D(fig, elev=-150, azim=110)
  pca = sklearn.decomposition.PCA(n_components=3, random_state=0x7ed1ae6e)

  ax.set_xlim(left=-1.2, right=1.2)
  ax.set_ylim(bottom=-1.2, top=1.2)
  ax.set_zlim(bottom=-1.2, top=1.2)

  # Fit coordinates
  pca.fit(np.concatenate(train_coords))
  pca.fit(np.concatenate(validate_coords))

  # Transform coordinates and print labels
  legend = []
  for i in range(0, len(dataset.LABELS)):
    color = COLOR_MAP(to_color(i))
    legend.append(mpatches.Patch(color=color, label=dataset.LABELS[i]))
  ax.legend(handles=legend, fontsize=8)

  all_coords = [ train_coords, validate_coords ]
  for coord_type in range(0, len(all_coords)):
    colors = []
    all_x = []
    all_y = []
    all_z = []

    coords = all_coords[coord_type]
    is_train = coord_type is 0
    for i in range(0, len(coords)):
      ds_coords = pca.transform(coords[i])

      x = ds_coords[:, 0]
      y = ds_coords[:, 1]
      z = ds_coords[:, 2]

      color = COLOR_MAP(to_color(i))

      colors += [ color ] * len(x)
      all_x.append(x)
      all_y.append(y)
      all_z.append(z)

    all_x = np.concatenate(all_x)
    all_y = np.concatenate(all_y)
    all_z = np.concatenate(all_z)

    marker = 'o' if is_train else '^'
    size = 5 if is_train else 8
    ax.scatter(all_x, all_y, all_z, c=colors, marker=marker,
               edgecolor='k', s=size, alpha=0.75, linewidths=0.0,
               edgecolors='none')

  if fname == None:
    plt.show()
  else:
    plt.savefig(fname=fname)
    print("Saved image to " + fname)

if __name__ == '__main__':
  import sys

  datasets, sequence_len = dataset.parse()
  siamese, _, _ = gradtype_model.create(sequence_len)
  siamese.load_weights(sys.argv[1])

  train_datasets, validate_datasets = dataset.split(datasets)
  train_coords = dataset.evaluate_model(siamese, train_datasets)
  validate_coords = dataset.evaluate_model(siamese, validate_datasets)
  fname = sys.argv[2] if len(sys.argv) >= 3 else  None
  pca(train_coords, validate_coords, fname)
