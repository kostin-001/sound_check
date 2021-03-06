# Generated by Django 3.0.5 on 2020-05-03 21:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_filename', models.CharField(max_length=250)),
                ('fingerprinted', models.BooleanField(default=False)),
                ('file_sha1', models.BinaryField()),
                ('file_path', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Fingerprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_sum', models.BinaryField()),
                ('time_offset', models.IntegerField()),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sound_check_app.Song')),
            ],
        ),
        migrations.AddIndex(
            model_name='fingerprint',
            index=models.Index(fields=['hash_sum'], name='sound_check_hash_su_fbcc1c_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='fingerprint',
            unique_together={('hash_sum', 'song', 'time_offset')},
        ),
    ]
