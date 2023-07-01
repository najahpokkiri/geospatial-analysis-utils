
# this script reads the indices created already either using python or ENVI or QGIS (in TIFF) and creates beautiful visualisation out of it


library(ggplot2)
library(stars)
library(scales)
## theme 
theme_set(theme_bw())

theme_for_map <- theme(
  axis.ticks = element_blank(),
  axis.text= element_blank(), 
  axis.line = element_blank(),
  panel.border = element_blank(),
  panel.grid.major = element_line(color='transparent'),
  panel.grid.minor = element_line(color='transparent'),
  panel.background = element_blank(),
  plot.background = element_rect(fill = "transparent",color='transparent'),
  legend.title = element_blank(),
  axis.title = element_blank(),
  plot.title = element_text(hjust = .55, vjust = -5, family = 'serif'),
  legend.position = c(.965,.18),
  legend.key.size = unit(.5, 'cm'), #change legend key size
  legend.key.height = unit(.5, 'cm'), #change legend key height
  legend.key.width = unit(.5, 'cm'), #change legend key width
  legend.text = element_text(size=5) #change legend text font size
)

# Directory paths
base_path <- "~/work/internships/meghna"
indices_dir <- file.path(base_path, "LT05_L1TP_145044_20100428_20161016_01_T1/145044_20100428_indices/python/")
images_dir <- file.path(base_path, "r_images")

# Define regex pattern for file matching
file_pattern <- ".*\\.tif$"

# Generate plots for each file using regex matching
files <- list.files(indices_dir, pattern = file_pattern, full.names = TRUE)


generate_plot = function(raster, breaks,file_name, images_dir){
  
  plot<- ggplot()+
    geom_stars(data = raster, downsample = 20)+
    scale_x_continuous(expand = c(0, 0)) + 
    scale_y_continuous(expand = c(0, 0))+
    
    scale_fill_fermenter(palette = "Spectral", breaks = round(breaks,2),direction = 1,
                         na.value=NA)+
    theme_for_map +
    labs(title = indice_name )
  
  #save the plot
  ggsave(
    file.path(output_path, file_name),
    plot = plot,
    device='tiff',
    width = 4.5, height = 4,
    dpi = 300,
    bg='#ffffff')
}

for ( i in 1:length(files) ){
  
  path =  files[[i]]
  raster <- read_stars(path)
  file_name <- basename(path)
  output_path = images_dir
  
  
  indice_name = sub(".*_(.*)\\.tif", "\\1", file_name, ignore.case = TRUE)
  breaks = unname(quantile(raster[[file_name]],  na.rm = TRUE, probs = seq(0, 1,.1)))
  
  
  generate_plot(raster, breaks,file_name, output_path)
  print(file_name)
  
}

