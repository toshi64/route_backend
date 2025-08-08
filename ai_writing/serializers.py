from rest_framework import serializers
from .models import QuestionClipForGrammar, GrammarQuestion, AnswerUnit, AIFeedback
from instant_feedback.models import Session
from material_scheduler.models import ScheduleComponent

class QuestionClipForGrammarSerializer(serializers.ModelSerializer):
    answer_unit_id = serializers.IntegerField(write_only=True)
    grammar_question_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = QuestionClipForGrammar
        fields = [
            'id', 'user', 'answer_unit_id', 'grammar_question_id',
            'content', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user

        # 必須：AnswerUnit を取得
        answer_unit_id = validated_data.pop('answer_unit_id')
        answer_unit = AnswerUnit.objects.get(id=answer_unit_id)

        # 任意：GrammarQuestion を取得
        grammar_question = None
        if 'grammar_question_id' in validated_data:
            grammar_question_id = validated_data.pop('grammar_question_id')
            grammar_question = GrammarQuestion.objects.filter(id=grammar_question_id).first()

        # 関連情報を AnswerUnit から引く
        session = answer_unit.session
        schedule_component = answer_unit.component

        return QuestionClipForGrammar.objects.create(
            user=user,
            answer_unit=answer_unit,
            grammar_question=grammar_question,
            session=session,
            schedule_component=schedule_component,
            **validated_data
        )





# GrammarQuestion（問題文、ジャンル、模範解答）
class GrammarQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarQuestion
        fields = ['id', 'question_text', 'genre', 'subgenre', 'answer']

# AIFeedback（AIのフィードバック）
class AIFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFeedback
        fields = ['feedback_text']

# AnswerUnit（ユーザーの回答、紐づくGrammarQuestionとAI Feedbackを含む）
class AnswerUnitSerializer(serializers.ModelSerializer):
    question = GrammarQuestionSerializer()
    ai_feedback = AIFeedbackSerializer()

    class Meta:
        model = AnswerUnit
        fields = ['id', 'user_answer', 'created_at', 'question', 'ai_feedback']

# QuestionClipForGrammar（疑問clipのメイン）
class QuestionClipDetailSerializer(serializers.ModelSerializer):
    answer_unit = AnswerUnitSerializer()

    class Meta:
        model = QuestionClipForGrammar
        fields = ['id', 'content', 'created_at', 'answer_unit']



class ReviewCandidateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='question.id')
    question_text = serializers.CharField(source='question.question_text')
    genre = serializers.CharField(source='question.genre')
    subgenre = serializers.CharField(source='question.subgenre')  # ✅ これを追加
    difficulty = serializers.IntegerField(source='question.difficulty')
    created_at = serializers.DateTimeField()

    class Meta:
        model = AnswerUnit
        fields = ['question_id', 'question_text', 'genre', 'subgenre', 'difficulty', 'created_at']



# ai_writing/serializers.py の末尾に以下を追加

from rest_framework import serializers
from .models import StraSession, StraCycleSession, GrammarQuestion, GrammarNote


class StraSessionSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = StraSession
        fields = [
            'id', 'user', 'material', 'target_cycles', 'completed_cycles',
            'status', 'session_date', 'started_at', 'completed_at',
            'progress_percentage', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        return obj.progress_percentage
    
    def get_is_completed(self, obj):
        return obj.is_completed


class StraCycleSessionSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    is_started = serializers.SerializerMethodField()
    
    class Meta:
        model = StraCycleSession
        fields = [
            'id', 'stra_session', 'cycle_index', 'material', 'session_id',
            'started_at', 'completed_at', 'is_completed', 'is_started'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_completed(self, obj):
        return obj.is_completed
    
    def get_is_started(self, obj):
        return obj.is_started


class GrammarQuestionSerializer(serializers.ModelSerializer):
    subgenre_name = serializers.CharField(source='subgenre_fk.name', read_only=True)
    
    class Meta:
        model = GrammarQuestion
        fields = [
            'id', 'custom_id', 'question_text', 'genre', 'subgenre_fk',
            'subgenre_name',  # 追加：Subgenreの名前
            'level', 'type', 'difficulty', 'importance', 'answer'
        ]


class GrammarNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarNote
        fields = [
            'id', 'custom_id', 'subgenre_fk', 'title', 'description'
        ]




# serializers.py
from collections import defaultdict
from rest_framework import serializers
from .models import StraSession, AnswerUnit

# ────────────────────────────────────────────────────────────
# 1. 周回履歴用サブシリアライザー
# ────────────────────────────────────────────────────────────
class CycleHistorySerializer(serializers.Serializer):
    cycle           = serializers.IntegerField()
    overallGrade    = serializers.CharField(allow_null=True)
    questionGrades  = serializers.ListField(child=serializers.CharField())
    completedAt     = serializers.DateTimeField()


# ────────────────────────────────────────────────────────────
# 2. セッション進捗シリアライザー（start_session で使用）
# ────────────────────────────────────────────────────────────
class SessionProgressSerializer(serializers.ModelSerializer):
    # モデルに無い値はすべて SerializerMethodField で算出
    currentCycle       = serializers.SerializerMethodField()
    totalCycles        = serializers.IntegerField(source='target_cycles')
    progressPercentage = serializers.SerializerMethodField()
    cycleHistory       = serializers.SerializerMethodField()

    class Meta:
        model  = StraSession
        fields = (
            'currentCycle',
            'totalCycles',
            'progressPercentage',
            'cycleHistory',
        )

    # -------------- 単純計算系 -----------------
    def get_currentCycle(self, obj: StraSession) -> int:
        # “今取り組む周回” = 完了済み + 1
        return obj.completed_cycles + 1

    def get_progressPercentage(self, obj: StraSession) -> int:
        return int(obj.progress_percentage)

    # -------------- 周回履歴 -------------------
    def get_cycleHistory(self, obj: StraSession):
        """
        完了済み StraCycleSession について
        - 各設問の grade を収集
        - overallGrade を平均から算出
        """
        # 1) AnswerUnit → grade 一括取得（StraSession 経由）
        aus = (AnswerUnit.objects
                  .filter(stra_cycle_session__stra_session=obj)
                  .select_related('evaluation', 'stra_cycle_session')
                  .values('stra_cycle_session__cycle_index',
                          'evaluation__overall_grade'))

        buckets = defaultdict(list)   # {cycle_index: ['A','B',...]}
        for row in aus:
            if row['evaluation__overall_grade']:
                buckets[row['stra_cycle_session__cycle_index']].append(
                    row['evaluation__overall_grade']
                )

        # 2) 完了済み Cycle を並べ替えて履歴リストを組立
        history = []
        cycles = (obj.cycle_sessions
                    .filter(completed_at__isnull=False)
                    .order_by('cycle_index'))

        for c in cycles:
            grades = buckets.get(c.cycle_index, [])
            history.append({
                "cycle":          c.cycle_index,
                "overallGrade":   _letter_avg(grades),
                "questionGrades": grades,
                "completedAt":    c.completed_at,
            })

        return CycleHistorySerializer(history, many=True).data


# ────────────────────────────────────────────────────────────
# 3. レター平均補助関数
# ────────────────────────────────────────────────────────────
_letter_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
_inv_letter = {v: k for k, v in _letter_map.items()}

def _letter_avg(grades):
    """
    ['A','C','B'] → 最近傍の平均レターを返す
    grade が空なら None
    """
    if not grades:
        return None
    score = sum(_letter_map[g] for g in grades) / len(grades)
    return _inv_letter[round(score)]
