from rest_framework import serializers
from .models import QuestionClipForGrammar, GrammarQuestion, AnswerUnit
from instant_feedback.models import Session
from material_scheduler.models import ScheduleComponent

class QuestionClipForGrammarSerializer(serializers.ModelSerializer):
    answer_unit_id = serializers.IntegerField(write_only=True)
    grammar_question_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = QuestionClipForGrammar
        fields = [
            'id', 'user', 'answer_unit_id', 'grammar_question_id',
            'title', 'content', 'created_at'
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
