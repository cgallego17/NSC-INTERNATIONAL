from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("media", "0002_mediafile_thumbnail"),
        ("locations", "0012_hotelroomimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="hotelroomimage",
            name="media_file",
            field=models.ForeignKey(
                blank=True,
                help_text="Archivo seleccionado desde la biblioteca multimedia",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="hotel_room_images",
                to="media.mediafile",
                verbose_name="Archivo Multimedia",
            ),
        ),
        migrations.AlterField(
            model_name="hotelroomimage",
            name="image",
            field=models.ImageField(
                blank=True,
                help_text="Imagen para la galería de la habitación",
                null=True,
                upload_to="hotels/rooms/gallery/",
                verbose_name="Imagen",
            ),
        ),
    ]


