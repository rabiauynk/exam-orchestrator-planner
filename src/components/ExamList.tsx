import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiClient, type Exam } from "@/lib/api";
import { Calendar, Clock, Computer, Loader2, Trash2, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export const ExamList = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  // Load exams on component mount
  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getExams();
      if (response.success && response.data) {
        setExams(response.data);
      } else {
        toast.error('Sınavlar yüklenirken hata oluştu');
      }
    } catch (error) {
      console.error('Error loading exams:', error);
      toast.error('Sınavlar yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteExam = async (examId: number) => {
    if (!confirm('Bu sınavı silmek istediğinizden emin misiniz?')) {
      return;
    }

    try {
      const response = await apiClient.deleteExam(examId);
      if (response.success) {
        toast.success('Sınav başarıyla silindi');
        // Reload exams
        loadExams();
      } else {
        toast.error(response.message || 'Sınav silinirken hata oluştu');
      }
    } catch (error) {
      console.error('Error deleting exam:', error);
      toast.error('Sınav silinirken hata oluştu');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "planned":
        return <Badge variant="default" className="bg-green-500">Planlandı</Badge>;
      case "pending":
        return <Badge variant="secondary">Beklemede</Badge>;
      case "completed":
        return <Badge variant="outline" className="bg-blue-500 text-white">Tamamlandı</Badge>;
      default:
        return <Badge variant="outline">Bilinmiyor</Badge>;
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('tr-TR');
    } catch {
      return dateStr;
    }
  };

  const formatTime = (timeStr: string) => {
    try {
      const time = new Date(`2000-01-01T${timeStr}`);
      return time.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timeStr;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Sınavlar yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ders</TableHead>
              <TableHead>Sınıf</TableHead>
              <TableHead>Hoca</TableHead>
              <TableHead>Öğrenci</TableHead>
              <TableHead>Süre</TableHead>
              <TableHead>Bilgisayar</TableHead>
              <TableHead>Durum</TableHead>
              <TableHead>Planlanmış</TableHead>
              <TableHead>İşlemler</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {exams.map((exam) => (
              <TableRow key={exam.id}>
                <TableCell className="font-medium">
                  <div>
                    <div>{exam.course_name || exam.course?.name}</div>
                    {exam.course?.credits && exam.course.credits >= 4 && (
                      <div className="text-xs text-orange-600">🔥 Zor Ders ({exam.course.credits} kredi)</div>
                    )}
                  </div>
                </TableCell>
                <TableCell>{exam.class_name || exam.course?.class_level}. Sınıf</TableCell>
                <TableCell>{exam.instructor}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {exam.student_count}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {exam.duration} dk
                  </div>
                </TableCell>
                <TableCell>
                  {exam.needs_computer ? (
                    <Computer className="h-4 w-4 text-blue-600" />
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </TableCell>
                <TableCell>{getStatusBadge(exam.status || 'pending')}</TableCell>
                <TableCell>
                  {exam.exam_schedules && exam.exam_schedules.length > 0 ? (
                    <div className="space-y-1">
                      {exam.exam_schedules.map((schedule, index) => (
                        <div key={index} className="space-y-1 border-b border-gray-100 pb-1 last:border-b-0">
                          <div className="flex items-center gap-1 text-sm">
                            <Calendar className="h-3 w-3" />
                            {formatDate(schedule.scheduled_date)}
                          </div>
                          <div className="flex items-center gap-1 text-sm text-gray-600">
                            <Clock className="h-3 w-3" />
                            {formatTime(schedule.start_time)} - {formatTime(schedule.end_time)}
                          </div>
                          <div className="text-xs text-gray-500">
                            📍 {schedule.room?.name}
                          </div>
                        </div>
                      ))}
                      {exam.exam_schedules.length > 1 && (
                        <div className="text-xs text-blue-600 font-medium">
                          🏢 {exam.exam_schedules.length} sınıfta
                        </div>
                      )}
                    </div>
                  ) : (
                    <span className="text-gray-400">Planlanmadı</span>
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => exam.id && handleDeleteExam(exam.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {exams.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          Henüz sınav eklenmedi. Yeni sınav eklemek için "Sınav Ekle" sekmesini kullanın.
        </div>
      )}
    </div>
  );
};
