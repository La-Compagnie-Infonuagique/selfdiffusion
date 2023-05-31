import pathlib
import os
import questionary


def review(folder, caption=False):

    # make a list of all the images in the folder
    path = pathlib.Path(folder)

    # assume that all the files in the folder are images
    files = [ f for f in path.iterdir() if f.is_file() ]

    def review_image(img_path, caption):

        # display the image on the command line using the imgcat command
        os.system('imgcat ' + str(img_path))

        # print the file path below the image
        print(img_path)

        # ask the user what he wants to do with the image (keep, delete)
        action = questionary.select('Do you want to keep this image?', choices=['keep', 'delete']).ask()

        if action == 'delete':
            img_path.unlink()
            return False
        else:
            if caption:
                caption = questionary.text('Enter a caption for the image').ask()
                caption_path = img_path.with_suffix('.txt')
                with open(caption_path, 'w') as f:
                    f.write(caption)
            return True

    # loop through all the images in the folder
    for img_path in files:
        review_image(img_path,caption)

    return


        



