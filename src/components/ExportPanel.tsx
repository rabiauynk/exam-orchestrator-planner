import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, type Exam } from "@/lib/api";
import { Calendar, Download, FileSpreadsheet, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import * as XLSX from 'xlsx';

interface DepartmentStats {
  id: number;
  name: string;
  code: string;
  examCount: number;
  plannedCount: number;
  lastUpdate: string;
}

export const ExportPanel = () => {
  const [departments, setDepartments] = useState<DepartmentStats[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState<number | null>(null);

  // Load departments and exams
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        // Load departments
        const deptResponse = await apiClient.getDepartments();
        const examResponse = await apiClient.getExams();

        if (deptResponse.success && examResponse.success && deptResponse.data && examResponse.data) {
          const deptData = deptResponse.data;
          const examData = examResponse.data;
          setExams(examData);

          // Calculate stats for each department
          const deptStats: DepartmentStats[] = deptData.map(dept => {
            const deptExams = examData.filter(exam => exam.department_id === dept.id);
            const plannedExams = deptExams.filter(exam => exam.status === 'planned');

            return {
              id: dept.id,
              name: dept.name,
              code: dept.code,
              examCount: deptExams.length,
              plannedCount: plannedExams.length,
              lastUpdate: new Date().toLocaleString('tr-TR')
            };
          });

          setDepartments(deptStats);
        }
      } catch (error) {
        console.error('Error loading data:', error);
        toast.error('Veriler yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatExamData = (exam: Exam) => {
    // Çoklu sınıf desteği için sınıf bilgilerini birleştir
    let roomInfo = 'Atanmadı';
    let dateInfo = 'Planlanmadı';
    let startTimeInfo = 'Planlanmadı';
    let endTimeInfo = 'Planlanmadı';

    if (exam.exam_schedules && exam.exam_schedules.length > 0) {
      const schedule = exam.exam_schedules[0]; // İlk schedule'dan tarih/saat al
      dateInfo = new Date(schedule.scheduled_date).toLocaleDateString('tr-TR');
      startTimeInfo = schedule.start_time;
      endTimeInfo = schedule.end_time;

      // Ana sınıf
      const rooms = [schedule.room?.name || 'Bilinmiyor'];
      let totalCapacity = schedule.room?.capacity || 0;

      // Ek sınıfları ekle
      if (schedule.additional_room_details && schedule.additional_room_details.length > 0) {
        schedule.additional_room_details.forEach(room => {
          rooms.push(room.name);
          totalCapacity += room.capacity;
        });
      }

      // Sınıf bilgisini formatla
      if (rooms.length > 1) {
        roomInfo = `${rooms.join(', ')} (Toplam: ${totalCapacity} kişi)`;
      } else {
        roomInfo = `${rooms[0]} (${totalCapacity} kişi)`;
      }
    }

    return {
      'Sınıf Seviyesi': exam.course?.class_level || 0,
      'Ders Adı': exam.course_name || exam.course?.name || 'Bilinmiyor',
      'Ders Kodu': exam.course?.code || 'Bilinmiyor',
      'Sınıf': exam.class_name || `${exam.course?.class_level}. Sınıf` || 'Bilinmiyor',
      'Hoca': exam.instructor,
      'Öğrenci Sayısı': exam.student_count,
      'Süre (dk)': exam.duration,
      'Tarih': dateInfo,
      'Başlangıç': startTimeInfo,
      'Bitiş': endTimeInfo,
      'Sınıf/Lab': roomInfo
    };
  };

  const handleExportDepartment = async (departmentId: number, departmentName: string) => {
    setExporting(departmentId);
    try {
      // Filter exams for this department
      const deptExams = exams.filter(exam => exam.department_id === departmentId);

      if (deptExams.length === 0) {
        toast.warning(`${departmentName} bölümünde henüz sınav bulunmuyor`);
        return;
      }

      // Sort exams by class level (1st year first), then by course name
      const sortedExams = deptExams.sort((a, b) => {
        // Önce sınıf seviyesine göre sırala (1, 2, 3, 4)
        const classLevelA = a.course?.class_level || 0;
        const classLevelB = b.course?.class_level || 0;

        if (classLevelA !== classLevelB) {
          return classLevelA - classLevelB;
        }

        // Aynı sınıf seviyesindeyse ders adına göre sırala
        const courseNameA = a.course?.name || '';
        const courseNameB = b.course?.name || '';
        return courseNameA.localeCompare(courseNameB, 'tr');
      });

      // Format data for Excel
      const excelData = sortedExams.map(formatExamData);

      // Remove the sorting column from Excel output
      const cleanedData = excelData.map(({ 'Sınıf Seviyesi': _, ...rest }) => rest);

      // Create workbook
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(cleanedData);

      // Add worksheet to workbook
      XLSX.utils.book_append_sheet(wb, ws, departmentName);

      // Generate filename
      const filename = `${departmentName}_Sinav_Programi_${new Date().toISOString().split('T')[0]}.xlsx`;

      // Download file
      XLSX.writeFile(wb, filename);

      toast.success(`${departmentName} sınav programı başarıyla indirildi!`);
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Dışa aktarım sırasında hata oluştu');
    } finally {
      setExporting(null);
    }
  };

  const handleExportAll = async () => {
    setExporting(-1);
    try {
      if (exams.length === 0) {
        toast.warning('Henüz sınav bulunmuyor');
        return;
      }

      // Create workbook
      const wb = XLSX.utils.book_new();

      // Add a sheet for each department
      departments.forEach(dept => {
        const deptExams = exams.filter(exam => exam.department_id === dept.id);
        if (deptExams.length > 0) {
          // Sort exams by class level (1st year first), then by course name
          const sortedExams = deptExams.sort((a, b) => {
            // Önce sınıf seviyesine göre sırala (1, 2, 3, 4)
            const classLevelA = a.course?.class_level || 0;
            const classLevelB = b.course?.class_level || 0;

            if (classLevelA !== classLevelB) {
              return classLevelA - classLevelB;
            }

            // Aynı sınıf seviyesindeyse ders adına göre sırala
            const courseNameA = a.course?.name || '';
            const courseNameB = b.course?.name || '';
            return courseNameA.localeCompare(courseNameB, 'tr');
          });

          const excelData = sortedExams.map(formatExamData);

          // Remove the sorting column from Excel output
          const cleanedData = excelData.map(({ 'Sınıf Seviyesi': _, ...rest }) => rest);

          const ws = XLSX.utils.json_to_sheet(cleanedData);
          XLSX.utils.book_append_sheet(wb, ws, dept.code);
        }
      });

      // Add summary sheet
      const summaryData = departments.map(dept => ({
        'Bölüm': dept.name,
        'Kod': dept.code,
        'Toplam Sınav': dept.examCount,
        'Planlanmış': dept.plannedCount,
        'Beklemede': dept.examCount - dept.plannedCount
      }));

      const summaryWs = XLSX.utils.json_to_sheet(summaryData);
      XLSX.utils.book_append_sheet(wb, summaryWs, 'Özet');

      // Generate filename
      const filename = `Tum_Bolumler_Sinav_Programi_${new Date().toISOString().split('T')[0]}.xlsx`;

      // Download file
      XLSX.writeFile(wb, filename);

      toast.success('Tüm bölümler sınav programı başarıyla indirildi!');
    } catch (error) {
      console.error('Export all error:', error);
      toast.error('Dışa aktarım sırasında hata oluştu');
    } finally {
      setExporting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Veriler yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Excel Dışa Aktarım</h3>
          <p className="text-gray-600">Her bölüm için ayrı sekmeli Excel dosyası oluşturun</p>
        </div>
        <Button
          onClick={handleExportAll}
          className="flex items-center gap-2"
          disabled={exporting !== null || exams.length === 0}
        >
          {exporting === -1 ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          Tümünü Dışa Aktar
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.map((dept) => (
          <Card key={dept.id}>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{dept.name}</CardTitle>
              <CardDescription className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <Badge variant="secondary">{dept.examCount} sınav</Badge>
                <Badge variant={dept.plannedCount === dept.examCount ? "default" : "destructive"}>
                  {dept.plannedCount} planlandı
                </Badge>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm text-gray-600">
                Son güncelleme: {dept.lastUpdate}
              </div>
              <Button
                variant="outline"
                size="sm"
                className="w-full flex items-center gap-2"
                onClick={() => handleExportDepartment(dept.id, dept.name)}
                disabled={exporting !== null || dept.examCount === 0}
              >
                {exporting === dept.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileSpreadsheet className="h-4 w-4" />
                )}
                Excel Oluştur
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dışa Aktarım Ayarları</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="text-sm">
              <strong>Excel Formatı:</strong> Her bölüm ayrı sekme olarak + Özet sekmesi
            </div>
            <div className="text-sm">
              <strong>İçerik:</strong> Ders adı/kodu, sınıf, hoca, öğrenci sayısı, süre, tarih/saat, sınıf/lab bilgisi
            </div>
            <div className="text-sm">
              <strong>Sıralama:</strong> Sınıf seviyesine göre (1. sınıf en üstte), sonra ders adına göre alfabetik
            </div>
            <div className="text-sm">
              <strong>Çoklu Sınıf:</strong> Birden fazla sınıfta yapılan sınavlar tek satırda gösterilir
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
