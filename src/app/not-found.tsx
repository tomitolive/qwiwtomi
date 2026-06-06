import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#000] text-white">
      <div className="text-center px-6">
        <h1 className="text-6xl md:text-8xl font-black mb-4 text-primary">404</h1>
        <h2 className="text-2xl md:text-3xl font-bold mb-6">هذه الصفحة غير موجودة</h2>
        <p className="text-gray-400 mb-8 max-w-md mx-auto">
          عذراً، الصفحة التي تبحث عنها لا يمكن إيجادها. قد تم حذفها أو تغيير عنوانها.
        </p>
        <Link
          href="/"
          className="inline-block px-8 py-3 bg-primary text-white font-bold rounded-lg hover:bg-primary/90 transition-colors"
        >
          العودة إلى الرئيسية
        </Link>
      </div>
    </div>
  );
}
