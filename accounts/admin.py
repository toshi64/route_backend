from django.contrib import admin, messages
from .models import CustomUser
from .line_push import push_message_to_user

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'line_user_id', 'line_display_name', 'first_ai_writing_done')
    actions = ['send_diagnosis_result']

    def send_diagnosis_result(self, request, queryset):
        for user in queryset:
            if not user.line_user_id:
                self.message_user(request, f"{user.email} は LINE ID 未登録のため送信不可", messages.WARNING)
                continue
            try:
                message = (
    '真理子さん、英作文おつかれさまでした。\n\n'
    '今回の答案、じっくり見させてもらいました。\n'
    '真理子さんの文章には、「ちゃんと伝えたい」という気持ちがしっかり表れていて、\n'
    'たとえば「go to the library」や「gets up」「watch the movie」など、\n'
    '基本の表現をきちんと使おうとしているのがとても伝わってきました。\n\n'
    'そして、何よりすごいのは、「前よりもできていること」がはっきり見えることです。\n'
    'たとえば「go → goes」「everyday → every day」といった点、\n'
    '一度間違えたあとに、しっかり修正できていましたね。\n'
    'これは本当に大きな成長です。\n\n'
    'そのうえで、今回は「ここを意識すると、さらにグッと伸びる！」というポイントを３つにまとめました。\n\n'
    '① 三人称単数の動詞の使い方\n'
    'たとえば「My friend go」ではなく「My friend goes」にする、というルールです。\n'
    'これは「主語が誰かによって、動詞の形が変わる」という英語ならではの考え方。\n'
    '最初はピンとこなくても大丈夫。「誰が」「どうする」のセットをたくさん練習すれば、\n'
    '少しずつ自然に身についていきます。\n\n'
    '② 前置詞の使い方\n'
    '英語では「at six（6時に）」「on weekends（週末に）」のように、\n'
    '時間や場所を表すときに使う「前置詞」がとても大切です。\n'
    'たとえば「on six」ではなく「at six」など、\n'
    '一見細かいけれど、英語らしさをつくる大事なポイントなんです。\n\n'
    '③ ニュアンスを伝える副詞のこと\n'
    'たとえば「Did you watch the movie?（映画を見ましたか？）」は正しい文ですが、\n'
    '「もう見ましたか？」と聞きたいときには「already」を入れるともっと自然になります。\n'
    '「Did you already watch the movie?」のように。\n'
    'こういうちょっとした言葉を足せるようになると、\n'
    '英語で「伝えたいこと」がどんどん伝えられるようになります。\n\n'
    'どれも、真理子さんが「英語で伝えたい！」と思っているからこそ出てくる課題です。\n'
    '最初から全部できる人なんていません。\n'
    'でも、一つひとつを「なるほど、そういうことか」と思いながら身につけていけば、\n'
    '英語の世界がどんどんクリアになっていきますよ。\n\n'
    'これからも、一緒に「わかる→使える」になる英語を積み上げていきましょう。\n\n'
    '上記の点について、練習問題を作成して送ることができますが、お送りしてよろしいですか？　よければ、「はい」とだけ返信してください。'
)

                push_message_to_user(user.line_user_id, message)
                self.message_user(request, f"{user.email} に送信成功", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"{user.email} 送信失敗: {e}", messages.ERROR)

    send_diagnosis_result.short_description = "診断結果をLINEで送る"
