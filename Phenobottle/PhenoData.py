class Database:
    @staticmethod
    def upload():
        global time_ojip, value_ojip, norm_ojip
        try:
            time_ojip = ", ".join(str(x) for x in time_ojip)
            value_ojip = ", ".join(str(x) for x in value_ojip)
            norm_ojip = ", ".join(str(x) for x in norm_ojip)
            with connection.cursor() as cursor:
                sql_time = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                sql = "INSERT INTO `Advanced Parameters` (`Time Now`, `Day Night`, `Optical Density RAW`, `Transmittance`, `Optical Density`, `Temperature`, `Light Intensity`, `Fo`, `F_300us`, `Fj`, `Fi`, `Fm`, `Fv`, `Fv/Fm`, `Vj`, `FmQa`, `Mo`, `PIabs`, `Fj - Fo`, `Fi - Fo`, `Fi - Fj`, `Fm - Fi`, `Fo / OD`, `Fj / OD`, `Fi / OD`, `Fm / OD`, `Fv / OD`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (sql_time, day_night, od_raw, transmittance, optical_density,  temperature, LIGHT_INTENSITY, fo, f_300us, fj,
                    fi, fm, variable_fluorescence, quantum_yield, vj, fm_qa, mo,
                    performance_index, fj_fo, fi_fo, fi_fj, fm_fi, fo_od, fj_od,
                    fi_od, fm_od, variable_fluorescence_od))
                sql = "INSERT INTO `OJIP Curves` (`Time Now`, `Day Night`, `Time OJIP`, `Raw OJIP`, `Normalised OJIP`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (sql_time, day_night, time_ojip, value_ojip, norm_ojip))
                print("Written to SQL Database")
            connection.commit()

        except:
            print("SQLdb not avaliable... check db server... writing to csv instead")

    def close_database(self):
        connection.close()


class Excel:
    @staticmethod
    def upload():
        global day_night
        worksheet_name = "Phenobottle_%s" % PHENOBOTTLE_NUMBER + '.csv'

        with open(worksheet_name, 'a') as f:
            try:
                writer = csv.writer(f)
                spreadsheet_time = str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                writer.writerow([spreadsheet_time, day_night, od_raw, transmittance, optical_density,  temperature,
                LIGHT_INTENSITY, fo, f_300us, fj, fi, fm, variable_fluorescence, quantum_yield, vj, fm_qa, mo,
                performance_index, fj_fo, fi_fo, fi_fj, fm_fi, fo_od, fj_od, fi_od, fm_od, variable_fluorescence_od,
                fm_qa_od, time_ojip, value_ojip, norm_ojip])
                print("Written to Local .csv")

            except:
                print("Failed to write to local csv file...")
        f.close()