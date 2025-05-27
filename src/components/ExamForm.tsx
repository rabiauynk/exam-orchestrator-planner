import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { apiClient, type Course, type Department } from "@/lib/api";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { CalendarIcon, Plus, X } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export const ExamForm = () => {
  const [selectedClassLevel, setSelectedClassLevel] = useState("");
  const [selectedCourse, setSelectedCourse] = useState("");
  const [instructor, setInstructor] = useState("");
  const [studentCount, setStudentCount] = useState("");
  const [duration, setDuration] = useState("");
  const [preferredTime, setPreferredTime] = useState("");
  const [needsComputer, setNeedsComputer] = useState(false);
  const [preferredDates, setPreferredDates] = useState<Date[]>([]);

  // Data states
  const [userDepartment, setUserDepartment] = useState<Department | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [examWeekStart, setExamWeekStart] = useState<Date | null>(null);
  const [examWeekEnd, setExamWeekEnd] = useState<Date | null>(null);

  // Load user department and exam week settings on component mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load user's department from localStorage
        const savedDepartment = localStorage.getItem('selectedDepartment');
        if (savedDepartment) {
          try {
            const dept = JSON.parse(savedDepartment);
            setUserDepartment(dept);
          } catch (error) {
            console.error('Error parsing saved department:', error);
            toast.error('Bölüm bilgisi okunamadı. Lütfen tekrar giriş yapın.');
            return;
          }
        } else {
          toast.error('Bölüm bilgisi bulunamadı. Lütfen tekrar giriş yapın.');
          return;
        }

        // Load exam week settings
        const examWeekResponse = await apiClient.getExamWeekSettings();
        if (examWeekResponse.success && examWeekResponse.data) {
          if (examWeekResponse.data.start_date) {
            setExamWeekStart(new Date(examWeekResponse.data.start_date));
          }
          if (examWeekResponse.data.end_date) {
            setExamWeekEnd(new Date(examWeekResponse.data.end_date));
          }
        }
      } catch (error) {
        console.error('Error loading initial data:', error);
        toast.error('Veriler yüklenirken hata oluştu');
      }
    };

    loadInitialData();
  }, []);

  // Load courses when user department or class level changes
  useEffect(() => {
    const loadCourses = async () => {
      if (!userDepartment) {
        setCourses([]);
        return;
      }

      setLoading(true);
      try {
        const params: any = { department_id: userDepartment.id };
        if (selectedClassLevel) {
          params.class_level = parseInt(selectedClassLevel);
        }

        const response = await apiClient.getCourses(params);
        if (response.success && response.data) {
          setCourses(response.data);
        }
      } catch (error) {
        console.error('Error loading courses:', error);
        toast.error('Dersler yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    loadCourses();
  }, [userDepartment, selectedClassLevel]);

  // Reset course selection when class level changes
  useEffect(() => {
    setSelectedCourse("");
  }, [selectedClassLevel]);

  const addPreferredDate = (date: Date | undefined) => {
    if (date && !preferredDates.some(d => d.getTime() === date.getTime())) {
      setPreferredDates([...preferredDates, date]);
    }
  };

  const removePreferredDate = (index: number) => {
    setPreferredDates(preferredDates.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedCourse || !userDepartment) {
      toast.error('Lütfen ders seçin');
      return;
    }

    if (preferredDates.length !== 3) {
      toast.error('Tam olarak 3 tercih tarihi seçmelisiniz');
      return;
    }

    setLoading(true);
    try {
      const examData = {
        course_id: parseInt(selectedCourse),
        instructor,
        student_count: parseInt(studentCount),
        duration: parseInt(duration),
        needs_computer: needsComputer,
        preferred_dates: preferredDates.map(date => date.toISOString().split('T')[0]),
        department_id: userDepartment.id
      };

      const response = await apiClient.createExam(examData);

      if (response.success) {
        toast.success('Sınav başarıyla eklendi!');

        // Form temizle
        setSelectedClassLevel("");
        setSelectedCourse("");
        setInstructor("");
        setStudentCount("");
        setDuration("");
        setNeedsComputer(false);
        setPreferredDates([]);
      } else {
        toast.error(response.message || 'Sınav eklenirken hata oluştu');
      }
    } catch (error) {
      console.error('Error creating exam:', error);
      toast.error('Sınav eklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Get selected course info for credits display
  const selectedCourseInfo = courses.find(c => c.id.toString() === selectedCourse);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {userDepartment && (
        <div className="p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900">Bölümünüz</h3>
          <p className="text-blue-700">{userDepartment.name} ({userDepartment.code})</p>
          <p className="text-sm text-blue-600 mt-1">
            Sadece bu bölüme ait dersleri ekleyebilirsiniz.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        <div className="space-y-2">
          <Label htmlFor="classLevel">Sınıf Seviyesi</Label>
          <Select value={selectedClassLevel} onValueChange={setSelectedClassLevel} disabled={!userDepartment}>
            <SelectTrigger>
              <SelectValue placeholder={userDepartment ? "Sınıf seçin" : "Bölüm bilgisi yükleniyor..."} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1. Sınıf</SelectItem>
              <SelectItem value="2">2. Sınıf</SelectItem>
              <SelectItem value="3">3. Sınıf</SelectItem>
              <SelectItem value="4">4. Sınıf</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2 md:col-span-2">
          <Label htmlFor="course">Ders</Label>
          <Select value={selectedCourse} onValueChange={setSelectedCourse} disabled={!userDepartment || loading}>
            <SelectTrigger>
              <SelectValue placeholder={
                loading ? "Dersler yükleniyor..." :
                !userDepartment ? "Bölüm bilgisi yükleniyor..." :
                courses.length === 0 ? "Bu kriterlerde ders bulunamadı" :
                "Ders seçin"
              } />
            </SelectTrigger>
            <SelectContent>
              {courses.map((course) => (
                <SelectItem key={course.id} value={course.id.toString()}>
                  {course.name} ({course.code}) - {course.credits} Kredi
                  {course.credits >= 4 && " 🔥"}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedCourseInfo && selectedCourseInfo.credits >= 4 && (
            <p className="text-sm text-orange-600">
              ⚠️ Bu ders zor kategorisinde ({selectedCourseInfo.credits} kredi) - aynı gün başka zor ders planlanamaz
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="instructor">Ders Hocası</Label>
          <Input
            id="instructor"
            type="text"
            value={instructor}
            onChange={(e) => setInstructor(e.target.value)}
            placeholder="Hoca adını girin"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="studentCount">Öğrenci Sayısı</Label>
          <Input
            id="studentCount"
            type="number"
            value={studentCount}
            onChange={(e) => setStudentCount(e.target.value)}
            placeholder="Öğrenci sayısını girin"
            min="1"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="duration">Süre (dakika)</Label>
          <Input
            id="duration"
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            placeholder="Sınav süresi (dakika)"
            min="1"
            required
          />
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="needsComputer"
          checked={needsComputer}
          onCheckedChange={setNeedsComputer}
        />
        <Label htmlFor="needsComputer">Bilgisayar İhtiyacı Var</Label>
      </div>

      <div className="space-y-3">
        <Label>Tercih Edilen Tarihler (Tam olarak 3 tarih seçin)</Label>
        {examWeekStart && examWeekEnd && (
          <p className="text-sm text-blue-600">
            Sınav haftası: {format(examWeekStart, "dd/MM/yyyy")} - {format(examWeekEnd, "dd/MM/yyyy")}
          </p>
        )}
        <div className="flex flex-wrap gap-2">
          {preferredDates.map((date, index) => (
            <div key={index} className="flex items-center gap-2 bg-blue-50 px-3 py-1 rounded-md">
              <span className="text-sm">{format(date, "dd/MM/yyyy")}</span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removePreferredDate(index)}
                className="h-auto p-0 hover:bg-transparent"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>

        <Popover>
          <PopoverTrigger asChild>
            <Button
              type="button"
              variant="outline"
              className={cn(
                "justify-start text-left font-normal",
                "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              Tarih ekle ({preferredDates.length} seçili)
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              onSelect={addPreferredDate}
              disabled={(date) => {
                // Geçmiş tarihler
                if (date < new Date()) return true;

                // Sınav haftası dışındaki tarihler
                if (examWeekStart && examWeekEnd) {
                  if (date < examWeekStart || date > examWeekEnd) return true;
                }

                // Zaten seçilmiş tarihler
                if (preferredDates.some(d => d.getTime() === date.getTime())) return true;

                return false;
              }}
              initialFocus
              className="pointer-events-auto"
            />
          </PopoverContent>
        </Popover>

        {preferredDates.length !== 3 && (
          <p className="text-sm text-red-600">
            Tam olarak 3 tercih tarihi seçmelisiniz. (Şu an: {preferredDates.length})
          </p>
        )}

        {preferredDates.length === 3 && (
          <p className="text-sm text-green-600">
            ✓ 3 tercih tarihi seçildi. Sınav ekleyebilirsiniz.
          </p>
        )}
      </div>

      <Button
        type="submit"
        className="w-full"
        disabled={preferredDates.length !== 3 || loading || !selectedCourse}
      >
        <Plus className="mr-2 h-4 w-4" />
        {loading ? 'Ekleniyor...' : 'Sınav Ekle'}
      </Button>
    </form>
  );
};
